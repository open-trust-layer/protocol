//! Specification 0012 Milestone 24 deterministic streaming/HTTP semantics.
//!
//! This module performs no network I/O.  HTTP and streaming state is supplied
//! explicitly by the conformance caller so security-sensitive behavior remains
//! reproducible and independent from any server/client framework.

use std::collections::{BTreeMap, BTreeSet};

use crate::{
    bundle,
    cbor::{self, Value},
    error::OlpError,
    json::{self, Json},
    proof_identity,
    record,
    sha256,
    transport,
    util::{hex_decode, hex_encode, is_absolute_uri},
};

const STREAM_TYPES: [&str; 6] = ["manifest", "record", "proof", "resource", "result", "end"];
const SINGLE_MEDIA: [&str; 2] = ["application/cbor", "application/json"];
const MAX_FRAMES: usize = 20_000;

fn malformed(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::malformed(reason, message)
}
fn unsupported(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::unsupported(reason, message)
}
fn get_bool(obj: &BTreeMap<String, Json>, key: &str, default: bool) -> Result<bool, OlpError> {
    match obj.get(key) {
        None => Ok(default),
        Some(Json::Bool(v)) => Ok(*v),
        Some(_) => Err(malformed("MALFORMED_INPUT", format!("{key} must be boolean"))),
    }
}
fn get_str<'a>(obj: &'a BTreeMap<String, Json>, key: &str) -> Result<&'a str, OlpError> {
    obj.get(key)
        .ok_or_else(|| malformed("MALFORMED_INPUT", format!("missing {key}")))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_INPUT", e))
}
fn optional_str_array(obj: &BTreeMap<String, Json>, key: &str, defaults: &[&str]) -> Result<Vec<String>, OlpError> {
    match obj.get(key) {
        None => Ok(defaults.iter().map(|s| (*s).to_string()).collect()),
        Some(Json::Array(items)) => items
            .iter()
            .map(|v| v.as_str().map(str::to_string).map_err(|e| malformed("MALFORMED_INPUT", e)))
            .collect(),
        Some(_) => Err(malformed("MALFORMED_INPUT", format!("{key} must be an array"))),
    }
}

fn validate_frame(frame: &BTreeMap<String, Json>) -> Result<&str, OlpError> {
    if let Some(domain) = frame.get("domain") {
        if domain.as_str().map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))? != "OLP-FRAME" {
            return Err(malformed("MALFORMED_STREAM_FRAME", "invalid streaming frame discriminator"));
        }
    }
    if let Some(version) = frame.get("version") {
        let v = version.as_i64().map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?;
        if v != 1 {
            return Err(unsupported("UNSUPPORTED_STREAM_FRAME_VERSION", "unsupported streaming frame version"));
        }
    }
    let ty = frame
        .get("type")
        .ok_or_else(|| malformed("MALFORMED_STREAM_FRAME", "missing streaming frame type"))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?;
    if !STREAM_TYPES.contains(&ty) {
        return Err(unsupported("UNSUPPORTED_STREAM_FRAME_TYPE", "unsupported streaming frame type"));
    }
    Ok(ty)
}

fn encode_ojve_projection(value: &Json) -> Result<Json, OlpError> {
    let mut input = Json::object();
    input.insert("value".into(), value.clone());
    let output = transport::operation("encode_ojve", &Json::Object(input))?;
    Ok(output
        .get("ojve")
        .map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?
        .clone())
}

fn frame_wire(frame_type: &str, payload: &Json) -> Result<(Vec<u8>, Vec<u8>), OlpError> {
    if !STREAM_TYPES.contains(&frame_type) {
        return Err(unsupported("UNSUPPORTED_STREAM_FRAME_TYPE", "unsupported streaming frame type"));
    }
    let ojve = encode_ojve_projection(payload)?;
    let mut json_frame = Json::object();
    json_frame.insert("olpFrame".into(), Json::Int(1));
    json_frame.insert("payload".into(), ojve);
    json_frame.insert("type".into(), Json::String(frame_type.into()));
    let text = json::stringify(&Json::Object(json_frame));
    let mut json_seq = Vec::with_capacity(text.len() + 2);
    json_seq.push(0x1e);
    json_seq.extend_from_slice(text.as_bytes());
    json_seq.push(b'\n');

    let abstract_payload = cbor::from_adapter_json(payload)
        .map_err(|e| unsupported("UNSUPPORTED_STREAM_CBOR_VALUE", e))?;
    let cbor_item = cbor::encode(&Value::Array(vec![
        Value::Text("OLP-FRAME".into()),
        Value::Int(1),
        Value::Text(frame_type.into()),
        abstract_payload,
    ]))
    .map_err(|e| unsupported("UNSUPPORTED_STREAM_CBOR_VALUE", e))?;
    Ok((json_seq, cbor_item))
}

fn encode_stream_frame(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let ty = get_str(obj, "frame_type")?;
    let payload = obj.get("payload").unwrap_or(&Json::Null);
    let (json_seq, cbor_item) = frame_wire(ty, payload)?;
    let mut out = Json::object();
    out.insert("json_seq_hex".into(), Json::String(hex_encode(&json_seq)));
    out.insert("cbor_item_hex".into(), Json::String(hex_encode(&cbor_item)));
    Ok(Json::Object(out))
}

fn encode_stream_sequence(input: &Json) -> Result<Json, OlpError> {
    let frames = input
        .get("frames")
        .map_err(|e| malformed("MALFORMED_INPUT", e))?
        .as_array()
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    if frames.len() > MAX_FRAMES {
        return Err(malformed("RESOURCE_LIMIT_EXCEEDED", "stream frame count exceeds implementation limit"));
    }
    let mut json_seq = Vec::new();
    let mut cbor_seq = Vec::new();
    for raw in frames {
        let obj = raw.as_object().map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?;
        let ty = validate_frame(obj)?;
        let payload = obj.get("payload").unwrap_or(&Json::Null);
        let (j, c) = frame_wire(ty, payload)?;
        json_seq.extend_from_slice(&j);
        cbor_seq.extend_from_slice(&c);
    }
    let mut out = Json::object();
    out.insert("frame_count".into(), Json::Int(frames.len() as i128));
    out.insert("json_seq_hex".into(), Json::String(hex_encode(&json_seq)));
    out.insert("cbor_seq_hex".into(), Json::String(hex_encode(&cbor_seq)));
    Ok(Json::Object(out))
}

fn process_bundle_stream(input: &Json) -> Result<Json, OlpError> {
    let input_obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let frames = input
        .get("frames")
        .map_err(|e| malformed("MALFORMED_INPUT", e))?
        .as_array()
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    if frames.is_empty() {
        return Err(malformed("STREAM_MANIFEST_MISSING", "manifested stream is empty"));
    }
    if frames.len() > MAX_FRAMES {
        return Err(malformed("RESOURCE_LIMIT_EXCEEDED", "stream frame count exceeds implementation limit"));
    }

    // Validate every frame before interpreting bundle semantics.
    let mut types = Vec::with_capacity(frames.len());
    for raw in frames {
        let obj = raw.as_object().map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?;
        types.push(validate_frame(obj)?.to_string());
    }
    if types[0] != "manifest" {
        return Err(malformed("STREAM_MANIFEST_NOT_FIRST", "first manifested-bundle frame must be manifest"));
    }

    let mut manifest_count = 0usize;
    let mut manifest_record: Option<Json> = None;
    let mut records = Vec::new();
    let mut proofs = Vec::new();
    let mut resources = Vec::new();
    let mut result_count = 0usize;
    let mut end_seen = false;
    let mut present_record_ids = Vec::new();
    let mut present_proof_ids = Vec::new();
    let mut present_resource_ids = Vec::new();

    for (index, raw) in frames.iter().enumerate() {
        let obj = raw.as_object().map_err(|e| malformed("MALFORMED_STREAM_FRAME", e))?;
        let ty = &types[index];
        if end_seen {
            return Err(malformed("STREAM_FRAME_AFTER_END", "semantic frame appears after end frame"));
        }
        match ty.as_str() {
            "manifest" => {
                manifest_count += 1;
                if manifest_record.is_none() {
                    manifest_record = Some(
                        obj.get("record")
                            .ok_or_else(|| malformed("MALFORMED_STREAM_MANIFEST", "manifest frame requires record"))?
                            .clone(),
                    );
                }
            }
            "record" => {
                let r = obj
                    .get("record")
                    .ok_or_else(|| malformed("MALFORMED_STREAM_RECORD", "record frame requires record"))?
                    .clone();
                present_record_ids.push(hex_encode(&record::identity_digest(&r)?));
                records.push(r);
            }
            "proof" => {
                let p = obj
                    .get("proof")
                    .ok_or_else(|| malformed("MALFORMED_STREAM_PROOF", "proof frame requires proof"))?
                    .clone();
                present_proof_ids.push(hex_encode(&proof_identity::proof_identity_digest_for(&p)?));
                proofs.push(p);
            }
            "resource" => {
                let rr = obj
                    .get("resource_ref")
                    .ok_or_else(|| malformed("MALFORMED_STREAM_RESOURCE", "resource frame requires resource_ref"))?
                    .clone();
                let content_hex = obj
                    .get("content_hex")
                    .ok_or_else(|| malformed("MALFORMED_STREAM_RESOURCE", "resource frame requires content_hex"))?
                    .clone();
                if let Json::Object(rr_obj) = &rr {
                    if let Some(Json::String(d)) = rr_obj.get("digest_hex") {
                        present_resource_ids.push(d.clone());
                    }
                }
                let mut item = Json::object();
                item.insert("resource_ref".into(), rr);
                item.insert("content_hex".into(), content_hex);
                resources.push(Json::Object(item));
            }
            "result" => result_count += 1,
            "end" => {
                end_seen = true;
                if index != frames.len() - 1 {
                    return Err(malformed("STREAM_FRAME_AFTER_END", "end frame must be final"));
                }
            }
            _ => unreachable!(),
        }
    }
    if manifest_count != 1 {
        return Err(malformed("DUPLICATE_STREAM_MANIFEST", "manifested stream must contain exactly one manifest"));
    }

    let mut bundle_input = Json::object();
    bundle_input.insert(
        "manifest_record".into(),
        manifest_record.ok_or_else(|| malformed("STREAM_MANIFEST_MISSING", "missing manifest record"))?,
    );
    bundle_input.insert("records".into(), Json::Array(records));
    bundle_input.insert("proofs".into(), Json::Array(proofs));
    bundle_input.insert("resources".into(), Json::Array(resources));
    if let Some(v) = input_obj.get("understood_critical_extensions") {
        bundle_input.insert("understood_critical_extensions".into(), v.clone());
    }
    let bundle_result = bundle::process_bundle_operation(&Json::Object(bundle_input))?;
    let bundle_obj = bundle_result.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let missing_items = bundle_obj
        .get("missing_items")
        .ok_or_else(|| malformed("MALFORMED_INPUT", "bundle result lacks missing_items"))?
        .as_array()
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let missing_resources = bundle_obj
        .get("missing_resources")
        .ok_or_else(|| malformed("MALFORMED_INPUT", "bundle result lacks missing_resources"))?
        .as_array()
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let truncated = get_bool(input_obj, "truncated", false)?;
    let transport_complete = !truncated && missing_items.is_empty() && missing_resources.is_empty();

    present_record_ids.sort();
    present_proof_ids.sort();
    present_resource_ids.sort();
    let mut out = Json::object();
    out.insert(
        "transport_status".into(),
        Json::String(if transport_complete { "COMPLETE" } else { "INCOMPLETE" }.into()),
    );
    out.insert("truncated".into(), Json::Bool(truncated));
    out.insert("end_frame_present".into(), Json::Bool(end_seen));
    out.insert("result_frame_count".into(), Json::Int(result_count as i128));
    out.insert("bundle".into(), bundle_result);
    out.insert(
        "present_record_identity_hex".into(),
        Json::Array(present_record_ids.into_iter().map(Json::String).collect()),
    );
    out.insert(
        "present_proof_identity_hex".into(),
        Json::Array(present_proof_ids.into_iter().map(Json::String).collect()),
    );
    out.insert(
        "present_resource_digest_hex".into(),
        Json::Array(present_resource_ids.into_iter().map(Json::String).collect()),
    );
    out.insert("present_objects_remain_individually_addressable".into(), Json::Bool(true));
    out.insert("frame_order_has_evidence_semantics".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

fn negotiate(accept: &[String], offered: &[String]) -> Result<Option<String>, OlpError> {
    for range in accept {
        if range.contains(';') {
            return Err(malformed("MALFORMED_HTTP_ACCEPT", "Accept fixtures must not contain parameters"));
        }
        if range == "*/*" {
            return Ok(offered.first().cloned());
        }
        if let Some(prefix) = range.strip_suffix('*') {
            if range.ends_with("/*") {
                if let Some(candidate) = offered.iter().find(|c| c.starts_with(prefix)) {
                    return Ok(Some(candidate.clone()));
                }
            }
        } else if offered.contains(range) {
            return Ok(Some(range.clone()));
        }
    }
    Ok(None)
}

fn auth_gate(authentication: &str, authorization: &str) -> Result<Option<(i128, &'static str)>, OlpError> {
    if !["NOT_REQUIRED", "SUCCEEDED", "MISSING", "FAILED"].contains(&authentication) {
        return Err(malformed("MALFORMED_HTTP_AUTH_STATE", "unknown HTTP authentication state"));
    }
    if !["NOT_APPLICABLE", "ALLOWED", "DENIED"].contains(&authorization) {
        return Err(malformed("MALFORMED_HTTP_AUTH_STATE", "unknown HTTP authorization state"));
    }
    if authentication == "MISSING" || authentication == "FAILED" {
        return Ok(Some((401, "HTTP_AUTHENTICATION_REQUIRED")));
    }
    if authorization == "DENIED" {
        return Ok(Some((403, "HTTP_AUTHORIZATION_DENIED")));
    }
    Ok(None)
}

fn decode_requested_identity(text: &str, expected_kind: &str) -> Result<Vec<u8>, OlpError> {
    let mut input = Json::object();
    input.insert("text".into(), Json::String(text.into()));
    input.insert("expected_kind".into(), Json::String(expected_kind.into()));
    let result = transport::operation("decode_identity_text", &Json::Object(input))?;
    let digest_hex = result
        .get("digest_hex")
        .map_err(|e| malformed("MALFORMED_IDENTITY_TEXT", e))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_IDENTITY_TEXT", e))?;
    hex_decode(digest_hex).map_err(|e| malformed("MALFORMED_IDENTITY_TEXT", e))
}

fn evaluate_http_read(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let kind = get_str(obj, "kind")?;
    if !["record", "proof", "bundle"].contains(&kind) {
        return Err(unsupported("UNSUPPORTED_HTTP_READ_KIND", "unsupported immutable HTTP read kind"));
    }
    let authentication = obj.get("authentication").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_HTTP_AUTH_STATE", e))?.unwrap_or("NOT_REQUIRED");
    let authorization = obj.get("authorization").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_HTTP_AUTH_STATE", e))?.unwrap_or("NOT_APPLICABLE");
    if let Some((status, reason)) = auth_gate(authentication, authorization)? {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(status));
        out.insert("reason".into(), Json::String(reason.into()));
        out.insert("authentication".into(), Json::String(authentication.into()));
        out.insert("authorization".into(), Json::String(authorization.into()));
        out.insert("global_nonexistence_established".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let accept = optional_str_array(obj, "accept", &SINGLE_MEDIA)?;
    let offered = optional_str_array(obj, "offered", &SINGLE_MEDIA)?;
    let Some(selected) = negotiate(&accept, &offered)? else {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(406));
        out.insert("reason".into(), Json::String("NOT_ACCEPTABLE".into()));
        out.insert("global_nonexistence_established".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    };
    let requested_text = get_str(obj, "requested_id_text")?;
    let expected_kind = if kind == "record" { "record" } else if kind == "proof" { "proof" } else { "bundle" };
    let requested = decode_requested_identity(requested_text, expected_kind)?;
    let Some(candidate) = obj.get("candidate") else {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(404));
        out.insert("reason".into(), Json::String("LOCAL_NOT_FOUND".into()));
        out.insert("response_media_type".into(), Json::Null);
        out.insert("global_nonexistence_established".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    };
    if matches!(candidate, Json::Null) {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(404));
        out.insert("reason".into(), Json::String("LOCAL_NOT_FOUND".into()));
        out.insert("response_media_type".into(), Json::Null);
        out.insert("global_nonexistence_established".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let digest = if kind == "proof" {
        proof_identity::proof_identity_digest_for(candidate)?.to_vec()
    } else {
        record::identity_digest(candidate)?.to_vec()
    };
    if digest != requested {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(422));
        out.insert("reason".into(), Json::String("IDENTITY_MISMATCH".into()));
        out.insert("identity_status".into(), Json::String("MISMATCH".into()));
        out.insert("response_media_type".into(), Json::Null);
        out.insert("global_nonexistence_established".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let mut out = Json::object();
    out.insert("http_status".into(), Json::Int(200));
    out.insert("reason".into(), Json::Null);
    out.insert("message_type".into(), Json::String(kind.into()));
    out.insert("identity_status".into(), Json::String("MATCH".into()));
    out.insert("response_media_type".into(), Json::String(selected));
    out.insert("authentication".into(), Json::String(authentication.into()));
    out.insert("authorization".into(), Json::String(authorization.into()));
    out.insert("global_nonexistence_established".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

fn evaluate_http_operation(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let operation = get_str(obj, "operation")?;
    if !["resolution", "disclosure", "bundleQuery"].contains(&operation) {
        return Err(unsupported("UNSUPPORTED_HTTP_OPERATION", "unsupported modeled HTTP operation"));
    }
    let semantic = get_str(obj, "semantic_status")?;
    let authentication = obj.get("authentication").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_HTTP_AUTH_STATE", e))?.unwrap_or("NOT_REQUIRED");
    let authorization = obj.get("authorization").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_HTTP_AUTH_STATE", e))?.unwrap_or("NOT_APPLICABLE");
    if let Some((status, reason)) = auth_gate(authentication, authorization)? {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(status));
        out.insert("reason".into(), Json::String(reason.into()));
        out.insert("semantic_status".into(), Json::String(semantic.into()));
        out.insert("semantic_status_evaluated".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let content_type = get_str(obj, "content_type")?;
    if !SINGLE_MEDIA.contains(&content_type) {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(415));
        out.insert("reason".into(), Json::String("UNSUPPORTED_MEDIA_TYPE".into()));
        out.insert("semantic_status".into(), Json::String(semantic.into()));
        out.insert("semantic_status_evaluated".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let accept = optional_str_array(obj, "accept", &SINGLE_MEDIA)?;
    let offered = optional_str_array(obj, "offered", &SINGLE_MEDIA)?;
    let Some(selected) = negotiate(&accept, &offered)? else {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(406));
        out.insert("reason".into(), Json::String("NOT_ACCEPTABLE".into()));
        out.insert("semantic_status".into(), Json::String(semantic.into()));
        out.insert("semantic_status_evaluated".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    };
    if operation == "bundleQuery" && get_bool(obj, "self_contained_required", false)? && !get_bool(obj, "self_contained_satisfied", true)? {
        let mut out = Json::object();
        out.insert("http_status".into(), Json::Int(422));
        out.insert("reason".into(), Json::String("SELF_CONTAINED_REQUIREMENT_UNSATISFIED".into()));
        out.insert("semantic_status".into(), Json::String(semantic.into()));
        out.insert("semantic_status_evaluated".into(), Json::Bool(true));
        out.insert("silent_profile_downgrade".into(), Json::Bool(false));
        return Ok(Json::Object(out));
    }
    let message_type = if operation == "resolution" { "resolutionResult" } else if operation == "disclosure" { "disclosureResult" } else { "bundle" };
    let mut out = Json::object();
    out.insert("http_status".into(), Json::Int(200));
    out.insert("reason".into(), Json::Null);
    out.insert("message_type".into(), Json::String(message_type.into()));
    out.insert("response_media_type".into(), Json::String(selected));
    out.insert("semantic_status".into(), Json::String(semantic.into()));
    out.insert("semantic_status_evaluated".into(), Json::Bool(true));
    out.insert("http_status_replaces_semantic_status".into(), Json::Bool(false));
    out.insert("silent_profile_downgrade".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

fn b64_value(byte: u8) -> Option<u8> {
    match byte {
        b'A'..=b'Z' => Some(byte - b'A'),
        b'a'..=b'z' => Some(byte - b'a' + 26),
        b'0'..=b'9' => Some(byte - b'0' + 52),
        b'+' => Some(62),
        b'/' => Some(63),
        _ => None,
    }
}
fn b64_encode(data: &[u8]) -> String {
    const T: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut out = String::new();
    let mut i = 0usize;
    while i + 3 <= data.len() {
        let n = ((data[i] as u32) << 16) | ((data[i + 1] as u32) << 8) | data[i + 2] as u32;
        out.push(T[((n >> 18) & 63) as usize] as char);
        out.push(T[((n >> 12) & 63) as usize] as char);
        out.push(T[((n >> 6) & 63) as usize] as char);
        out.push(T[(n & 63) as usize] as char);
        i += 3;
    }
    match data.len() - i {
        1 => {
            let n = (data[i] as u32) << 16;
            out.push(T[((n >> 18) & 63) as usize] as char);
            out.push(T[((n >> 12) & 63) as usize] as char);
            out.push('='); out.push('=');
        }
        2 => {
            let n = ((data[i] as u32) << 16) | ((data[i + 1] as u32) << 8);
            out.push(T[((n >> 18) & 63) as usize] as char);
            out.push(T[((n >> 12) & 63) as usize] as char);
            out.push(T[((n >> 6) & 63) as usize] as char);
            out.push('=');
        }
        _ => {}
    }
    out
}
fn b64_decode(text: &str) -> Result<Vec<u8>, OlpError> {
    if text.len() % 4 != 0 {
        return Err(malformed("MALFORMED_CONTENT_DIGEST", "base64 length must be multiple of four"));
    }
    let bytes = text.as_bytes();
    let mut out = Vec::new();
    for (chunk_index, chunk) in bytes.chunks_exact(4).enumerate() {
        let last = chunk_index + 1 == bytes.len() / 4;
        let pad = if chunk[3] == b'=' { if chunk[2] == b'=' { 2 } else { 1 } } else { 0 };
        if !last && pad != 0 { return Err(malformed("MALFORMED_CONTENT_DIGEST", "base64 padding before final group")); }
        if chunk[0] == b'=' || chunk[1] == b'=' { return Err(malformed("MALFORMED_CONTENT_DIGEST", "invalid base64 padding")); }
        let a = b64_value(chunk[0]).ok_or_else(|| malformed("MALFORMED_CONTENT_DIGEST", "invalid base64"))? as u32;
        let b = b64_value(chunk[1]).ok_or_else(|| malformed("MALFORMED_CONTENT_DIGEST", "invalid base64"))? as u32;
        let c = if chunk[2] == b'=' { 0 } else { b64_value(chunk[2]).ok_or_else(|| malformed("MALFORMED_CONTENT_DIGEST", "invalid base64"))? as u32 };
        let d = if chunk[3] == b'=' { 0 } else { b64_value(chunk[3]).ok_or_else(|| malformed("MALFORMED_CONTENT_DIGEST", "invalid base64"))? as u32 };
        let n = (a << 18) | (b << 12) | (c << 6) | d;
        out.push((n >> 16) as u8);
        if pad < 2 { out.push((n >> 8) as u8); }
        if pad == 0 { out.push(n as u8); }
    }
    if b64_encode(&out) != text {
        return Err(malformed("MALFORMED_CONTENT_DIGEST", "non-canonical base64"));
    }
    Ok(out)
}

fn validate_content_digest(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let content = hex_decode(obj.get("content_hex").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_INPUT", e))?.unwrap_or(""))
        .map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let required = get_bool(obj, "required", false)?;
    let Some(header) = obj.get("header_value") else {
        let mut out = Json::object();
        out.insert("status".into(), Json::String(if required { "MISSING" } else { "NOT_PRESENT" }.into()));
        out.insert("algorithm".into(), Json::Null);
        return Ok(Json::Object(out));
    };
    if matches!(header, Json::Null) {
        let mut out = Json::object();
        out.insert("status".into(), Json::String(if required { "MISSING" } else { "NOT_PRESENT" }.into()));
        out.insert("algorithm".into(), Json::Null);
        return Ok(Json::Object(out));
    }
    let header = header.as_str().map_err(|e| malformed("MALFORMED_CONTENT_DIGEST", e))?;
    if header.is_empty() { return Err(malformed("MALFORMED_CONTENT_DIGEST", "empty Content-Digest")); }
    let mut members: BTreeMap<String, Vec<u8>> = BTreeMap::new();
    for member in header.split(',').map(str::trim) {
        let Some(marker) = member.find("=:") else { return Err(malformed("MALFORMED_CONTENT_DIGEST", "malformed Content-Digest member")); };
        if !member.ends_with(':') { return Err(malformed("MALFORMED_CONTENT_DIGEST", "malformed Content-Digest member")); }
        let alg = &member[..marker];
        if alg.is_empty() || !alg.bytes().all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_' || b == b'-') {
            return Err(malformed("MALFORMED_CONTENT_DIGEST", "invalid digest algorithm token"));
        }
        if members.contains_key(alg) { return Err(malformed("MALFORMED_CONTENT_DIGEST", "duplicate digest algorithm")); }
        let encoded = &member[marker + 2..member.len() - 1];
        let decoded = b64_decode(encoded)?;
        if alg == "sha-256" && decoded.len() != 32 {
            return Err(malformed("MALFORMED_CONTENT_DIGEST", "sha-256 Content-Digest must contain exactly 32 octets"));
        }
        members.insert(alg.to_string(), decoded);
    }
    let Some(observed) = members.get("sha-256") else {
        let mut out = Json::object();
        out.insert("status".into(), Json::String(if required { "UNSUPPORTED" } else { "UNVALIDATED" }.into()));
        out.insert("algorithm".into(), Json::Null);
        return Ok(Json::Object(out));
    };
    let expected = sha256::digest(&content);
    let mut out = Json::object();
    out.insert("status".into(), Json::String(if observed.as_slice() == expected { "VALID" } else { "MISMATCH" }.into()));
    out.insert("algorithm".into(), Json::String("sha-256".into()));
    out.insert("expected_digest_hex".into(), Json::String(hex_encode(&expected)));
    out.insert("observed_digest_hex".into(), Json::String(hex_encode(observed)));
    Ok(Json::Object(out))
}

#[derive(Clone)]
struct ParsedUri { scheme: String, host: String, port: u16, path: String }
fn parse_http_uri(uri: &str) -> Result<ParsedUri, OlpError> {
    if !is_absolute_uri(uri) { return Err(malformed("MALFORMED_HTTP_REDIRECT", "redirect URI must be absolute")); }
    let Some(colon) = uri.find(':') else { return Err(malformed("MALFORMED_HTTP_REDIRECT", "missing URI scheme")); };
    let scheme = uri[..colon].to_ascii_lowercase();
    if scheme != "http" && scheme != "https" { return Err(malformed("MALFORMED_HTTP_REDIRECT", "redirect URI must use HTTP or HTTPS")); }
    let rest = &uri[colon + 1..];
    if !rest.starts_with("//") { return Err(malformed("MALFORMED_HTTP_REDIRECT", "HTTP URI must contain authority")); }
    let rest = &rest[2..];
    let split = rest.find(|c| c == '/' || c == '?' || c == '#').unwrap_or(rest.len());
    let authority = &rest[..split];
    if authority.is_empty() || authority.contains('@') { return Err(malformed("MALFORMED_HTTP_REDIRECT", "invalid HTTP authority")); }
    let path = if split < rest.len() { rest[split..].split(['?', '#']).next().unwrap_or("").to_string() } else { String::new() };
    let (host, port) = if authority.starts_with('[') {
        let end = authority.find(']').ok_or_else(|| malformed("MALFORMED_HTTP_REDIRECT", "invalid IPv6 authority"))?;
        let host = authority[..=end].to_ascii_lowercase();
        let suffix = &authority[end + 1..];
        let port = if suffix.is_empty() { if scheme == "https" { 443 } else { 80 } } else {
            let p = suffix.strip_prefix(':').ok_or_else(|| malformed("MALFORMED_HTTP_REDIRECT", "invalid authority"))?;
            p.parse::<u16>().map_err(|_| malformed("MALFORMED_HTTP_REDIRECT", "invalid port"))?
        };
        (host, port)
    } else {
        let mut parts = authority.rsplitn(2, ':');
        let last = parts.next().unwrap();
        if let Some(host_part) = parts.next() {
            let port = last.parse::<u16>().map_err(|_| malformed("MALFORMED_HTTP_REDIRECT", "invalid port"))?;
            (host_part.to_ascii_lowercase(), port)
        } else {
            (last.to_ascii_lowercase(), if scheme == "https" { 443 } else { 80 })
        }
    };
    if host.is_empty() { return Err(malformed("MALFORMED_HTTP_REDIRECT", "empty host")); }
    Ok(ParsedUri { scheme, host, port, path })
}

fn evaluate_redirect(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let method = get_str(obj, "method")?.to_ascii_uppercase();
    let original = parse_http_uri(get_str(obj, "original_uri")?)?;
    let target = parse_http_uri(get_str(obj, "location")?)?;
    if original.scheme == "https" && target.scheme == "http" {
        return Ok(blocked_redirect("HTTPS_DOWNGRADE"));
    }
    if method != "GET" && method != "HEAD" && !get_bool(obj, "allow_sensitive_post_redirect", false)? {
        return Ok(blocked_redirect("SENSITIVE_METHOD_REDIRECT_BLOCKED"));
    }
    if let Some(Json::String(requested)) = obj.get("requested_identity_text") {
        let target_last = target.path.trim_end_matches('/').rsplit('/').next().unwrap_or("");
        if target_last != requested { return Ok(blocked_redirect("REDIRECT_IDENTITY_CHANGED")); }
    } else if obj.get("requested_identity_text").is_some() {
        return Err(malformed("MALFORMED_HTTP_REDIRECT", "requested identity must be text"));
    }
    let same_origin = original.scheme == target.scheme && original.host == target.host && original.port == target.port;
    let credentials = get_bool(obj, "credentials_present", false)?;
    let forward = credentials && (same_origin || get_bool(obj, "allow_cross_origin_credentials", false)?);
    let mut out = Json::object();
    out.insert("status".into(), Json::String("ALLOWED".into()));
    out.insert("reason".into(), Json::Null);
    out.insert("same_origin".into(), Json::Bool(same_origin));
    out.insert("forward_credentials".into(), Json::Bool(forward));
    Ok(Json::Object(out))
}
fn blocked_redirect(reason: &str) -> Json {
    let mut out = Json::object();
    out.insert("status".into(), Json::String("BLOCKED".into()));
    out.insert("reason".into(), Json::String(reason.into()));
    out.insert("forward_credentials".into(), Json::Bool(false));
    Json::Object(out)
}

fn separate_auth(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let authn = get_str(obj, "http_authentication")?;
    let authz = get_str(obj, "service_authorization")?;
    auth_gate(authn, authz)?;
    let crypto = get_str(obj, "olp_cryptographic_validity")?;
    let authority = obj.get("olp_authority_evidence").map(|v| v.as_str()).transpose().map_err(|e| malformed("MALFORMED_OLP_STATUS", e))?.unwrap_or("NOT_EVALUATED");
    if crypto.is_empty() || authority.is_empty() { return Err(malformed("MALFORMED_OLP_STATUS", "OLP status must be non-empty")); }
    let mut out = Json::object();
    out.insert("http_authentication".into(), Json::String(authn.into()));
    out.insert("service_authorization".into(), Json::String(authz.into()));
    out.insert("olp_cryptographic_validity".into(), Json::String(crypto.into()));
    out.insert("olp_authority_evidence".into(), Json::String(authority.into()));
    out.insert("http_authentication_changes_olp_validity".into(), Json::Bool(false));
    out.insert("olp_proof_grants_http_authorization".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

fn evaluate_cache(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let reps = obj
        .get("representations_hex")
        .ok_or_else(|| malformed("MALFORMED_HTTP_CACHE_INPUT", "missing representations"))?
        .as_object()
        .map_err(|e| malformed("MALFORMED_HTTP_CACHE_INPUT", e))?;
    if reps.is_empty() { return Err(malformed("MALFORMED_HTTP_CACHE_INPUT", "representations must be non-empty")); }
    let mut validators = Json::object();
    let mut bodies = BTreeSet::new();
    for (media, value) in reps {
        if !media.contains('/') { return Err(malformed("MALFORMED_HTTP_CACHE_INPUT", "malformed media type")); }
        let bytes = hex_decode(value.as_str().map_err(|e| malformed("MALFORMED_HTTP_CACHE_INPUT", e))?)
            .map_err(|e| malformed("MALFORMED_HTTP_CACHE_INPUT", e))?;
        let etag = format!("\"repr-sha256-{}\"", hex_encode(&sha256::digest(&bytes)));
        validators.insert(media.clone(), Json::String(etag));
        bodies.insert(bytes);
    }
    let sensitive = get_bool(obj, "sensitive", false)?;
    let public_requested = get_bool(obj, "public_cache_requested", false)?;
    let explicit = get_bool(obj, "explicit_public_cache_policy", false)?;
    let mut out = Json::object();
    out.insert("representation_etags".into(), Json::Object(validators));
    out.insert("byte_distinct_representations".into(), Json::Bool(bodies.len() > 1));
    out.insert("object_identity_automatically_reused_as_strong_etag".into(), Json::Bool(false));
    out.insert("public_cache_allowed".into(), Json::Bool(!sensitive || !public_requested || explicit));
    out.insert("sensitive".into(), Json::Bool(sensitive));
    out.insert("explicit_public_cache_policy".into(), Json::Bool(explicit));
    Ok(Json::Object(out))
}

fn evaluate_range(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let partial = get_bool(obj, "partial_representation", false)?;
    let requested = get_bool(obj, "full_object_verification_requested", false)?;
    let blocked = partial && requested;
    let mut out = Json::object();
    out.insert("partial_representation".into(), Json::Bool(partial));
    out.insert("full_object_verification_requested".into(), Json::Bool(requested));
    out.insert("can_verify_full_olp_object".into(), Json::Bool(!partial));
    out.insert("verification_blocked".into(), Json::Bool(blocked));
    out.insert("reason".into(), if blocked { Json::String("PARTIAL_REPRESENTATION_NOT_FULL_OBJECT".into()) } else { Json::Null });
    Ok(Json::Object(out))
}

fn evaluate_limit(input: &Json) -> Result<Json, OlpError> {
    let observed = input.get("observed_bytes").map_err(|e| malformed("MALFORMED_HTTP_LIMIT", e))?.as_u64().map_err(|e| malformed("MALFORMED_HTTP_LIMIT", e))?;
    let max = input.get("max_bytes").map_err(|e| malformed("MALFORMED_HTTP_LIMIT", e))?.as_u64().map_err(|e| malformed("MALFORMED_HTTP_LIMIT", e))?;
    let exceeded = observed > max;
    let mut out = Json::object();
    out.insert("http_status".into(), Json::Int(if exceeded { 413 } else { 200 }));
    out.insert("limit_exceeded".into(), Json::Bool(exceeded));
    out.insert("evidence_invalid".into(), Json::Bool(false));
    out.insert("observed_bytes".into(), Json::Int(observed as i128));
    out.insert("max_bytes".into(), Json::Int(max as i128));
    Ok(Json::Object(out))
}

fn evaluate_rate_limit(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let limited = get_bool(obj, "limited", false)?;
    let retry = match obj.get("retry_after_seconds") {
        None | Some(Json::Null) => None,
        Some(v) => Some(v.as_u64().map_err(|e| malformed("MALFORMED_HTTP_RATE_LIMIT", e))?),
    };
    let mut out = Json::object();
    out.insert("http_status".into(), Json::Int(if limited { 429 } else { 200 }));
    out.insert("rate_limited".into(), Json::Bool(limited));
    out.insert("retry_after_seconds".into(), if limited { retry.map(|v| Json::Int(v as i128)).unwrap_or(Json::Null) } else { Json::Null });
    out.insert("evidence_invalid".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

pub fn operation(name: &str, input: &Json) -> Result<Json, OlpError> {
    match name {
        "encode_stream_frame" => encode_stream_frame(input),
        "encode_stream_sequence" => encode_stream_sequence(input),
        "process_bundle_stream" => process_bundle_stream(input),
        "evaluate_http_read" => evaluate_http_read(input),
        "evaluate_http_operation" => evaluate_http_operation(input),
        "validate_content_digest" => validate_content_digest(input),
        "evaluate_http_redirect" => evaluate_redirect(input),
        "separate_http_auth_from_olp" => separate_auth(input),
        "evaluate_http_cache" => evaluate_cache(input),
        "evaluate_http_range" => evaluate_range(input),
        "evaluate_http_limit" => evaluate_limit(input),
        "evaluate_http_rate_limit" => evaluate_rate_limit(input),
        _ => Err(unsupported("UNSUPPORTED_OPERATION", name)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn digest_transport_failure_never_becomes_evidence_invalidity() {
        let content = b"payload";
        let mut input = Json::object();
        input.insert("header_value".into(), Json::String("sha-256=:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=:".into()));
        input.insert("content_hex".into(), Json::String(hex_encode(content)));
        input.insert("required".into(), Json::Bool(true));
        let result = validate_content_digest(&Json::Object(input)).unwrap();
        assert_eq!(result.get("status").unwrap().as_str().unwrap(), "MISMATCH");
    }

    #[test]
    fn partial_range_never_claims_full_object_verification() {
        let mut input = Json::object();
        input.insert("partial_representation".into(), Json::Bool(true));
        input.insert("full_object_verification_requested".into(), Json::Bool(true));
        let result = evaluate_range(&Json::Object(input)).unwrap();
        assert!(!result.get("can_verify_full_olp_object").unwrap().as_bool().unwrap());
    }
}
