//! Specification 0009 deterministic, offline-first resolution core.
//!
//! This module consumes caller-supplied resolver snapshots. It performs no network I/O.

use std::collections::{BTreeMap, BTreeSet};
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};

use crate::{error::OlpError, json::Json, proof_identity, record, sha256, time, util::{hex_decode, hex_encode, is_absolute_uri}};

const DOMAIN: &str = "OLP-RESOLUTION-REQUEST";
const CORE_TARGETS: [&str; 6] = ["evidence", "verificationMethod", "principal", "externalResource", "lifecycle", "service"];

#[derive(Clone, Debug, PartialEq, Eq)]
struct EvidenceRef { kind: i64, digest: [u8; 32] }

#[derive(Clone, Debug, PartialEq, Eq)]
struct ResourceRef { resource_id: Option<String>, media_type: String, algorithm: i64, digest: [u8; 32] }

#[derive(Clone, Debug)]
struct Request {
    target_class: String,
    target: Json,
    accept: Vec<String>,
    offline_only: bool,
    max_bytes: Option<u64>,
    max_results: Option<u64>,
    allow_redirects: bool,
    require_fresh: bool,
}

fn malformed(reason: &str, msg: impl Into<String>) -> OlpError { OlpError::malformed(reason, msg) }
fn unsupported(reason: &str, msg: impl Into<String>) -> OlpError { OlpError::unsupported(reason, msg) }

fn parse_digest_hex(s: &str, reason: &str) -> Result<[u8; 32], OlpError> {
    let raw = hex_decode(s).map_err(|e| malformed(reason, e))?;
    raw.try_into().map_err(|_| malformed(reason, "digest must contain 32 octets"))
}

fn parse_evidence_ref(v: &Json) -> Result<EvidenceRef, OlpError> {
    let o = v.as_object().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let kind = o.get("kind").ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "missing evidence kind"))?
        .as_i64().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    if kind != 0 && kind != 1 { return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "unsupported evidence kind")); }
    let digest = parse_digest_hex(
        o.get("identity_digest_hex").ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "missing identity digest"))?
            .as_str().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?,
        "MALFORMED_RESOLUTION_REQUEST",
    )?;
    Ok(EvidenceRef { kind, digest })
}

fn ref_json(r: &EvidenceRef) -> Json {
    let mut o = Json::object();
    o.insert("kind".into(), Json::Int(r.kind as i128));
    o.insert("identity_digest_hex".into(), Json::String(hex_encode(&r.digest)));
    Json::Object(o)
}

fn valid_media_type(s: &str) -> bool {
    let mut it = s.split('/');
    let a = it.next().unwrap_or(""); let b = it.next().unwrap_or("");
    if a.is_empty() || b.is_empty() || it.next().is_some() { return false; }
    fn ok(x: &str) -> bool { x.bytes().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || b"!#$&^_.+-".contains(&c)) }
    ok(a) && ok(b)
}

fn parse_resource_ref(v: &Json) -> Result<ResourceRef, OlpError> {
    let o = v.as_object().map_err(|e| malformed("MALFORMED_RESOURCE_REF", e))?;
    let resource_id = match o.get("resource_id") {
        None | Some(Json::Null) => None,
        Some(Json::String(s)) => {
            if !is_absolute_uri(s) { return Err(malformed("MALFORMED_RESOURCE_REF", "resource id must be absolute URI")); }
            Some(s.clone())
        }
        Some(_) => return Err(malformed("MALFORMED_RESOURCE_REF", "resource id must be URI or null")),
    };
    let media_type = o.get("media_type").ok_or_else(|| malformed("MALFORMED_RESOURCE_REF", "missing media type"))?
        .as_str().map_err(|e| malformed("MALFORMED_RESOURCE_REF", e))?.to_string();
    if !valid_media_type(&media_type) { return Err(malformed("MALFORMED_RESOURCE_REF", "invalid media type")); }
    let algorithm = match o.get("hash_algorithm") {
        None => -16,
        Some(v) => v.as_i64().map_err(|e| malformed("MALFORMED_RESOURCE_REF", e))?,
    };
    if algorithm != -16 { return Err(unsupported("UNSUPPORTED_RESOURCE_HASH_ALGORITHM", "unsupported resource hash algorithm")); }
    let digest = parse_digest_hex(
        o.get("digest_hex").ok_or_else(|| malformed("MALFORMED_RESOURCE_REF", "missing digest"))?
            .as_str().map_err(|e| malformed("MALFORMED_RESOURCE_REF", e))?,
        "MALFORMED_RESOURCE_REF",
    )?;
    Ok(ResourceRef { resource_id, media_type, algorithm, digest })
}

fn parse_request(input: &Json) -> Result<Request, OlpError> {
    let r = input.get("request").map_err(|e| malformed("MALFORMED_INPUT", e))?;
    let o = r.as_object().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let domain = match o.get("domain") { None => DOMAIN, Some(v) => v.as_str().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))? };
    if domain != DOMAIN { return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "invalid resolution request discriminator")); }
    let version = match o.get("version") { None => 1, Some(v) => v.as_i64().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))? };
    if version != 1 { return Err(unsupported("UNSUPPORTED_RESOLUTION_REQUEST_VERSION", "unsupported resolution request version")); }
    let target_class = o.get("target_class").ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "missing target class"))?
        .as_str().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?.to_string();
    if !CORE_TARGETS.contains(&target_class.as_str()) {
        if is_absolute_uri(&target_class) { return Err(unsupported("UNSUPPORTED_TARGET_CLASS", "unsupported target class")); }
        return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "unknown compact target class"));
    }
    if target_class != "evidence" && target_class != "externalResource" {
        return Err(unsupported("UNSUPPORTED_TARGET_CLASS", "target class outside executable resolution-v1"));
    }
    let target = o.get("target").ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "missing target"))?.clone();
    if target_class == "evidence" { parse_evidence_ref(&target)?; }
    else {
        match &target {
            Json::String(s) => if !is_absolute_uri(s) { return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "external resource target must be absolute URI")); },
            Json::Object(m) if m.len() == 1 && m.contains_key("resource_ref") => { parse_resource_ref(m.get("resource_ref").unwrap())?; },
            _ => return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "external resource target malformed")),
        }
    }
    let accept = match o.get("accept") {
        None => Vec::new(),
        Some(Json::Array(a)) => {
            let mut seen = BTreeSet::new(); let mut out = Vec::new();
            for v in a { let s = v.as_str().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?; if s.is_empty() || !seen.insert(s.to_string()) { return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "invalid accept set")); } out.push(s.to_string()); }
            out
        }
        Some(_) => return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "accept must be array")),
    };
    if let Some(v) = o.get("as_of") { if !matches!(v, Json::Null) { let s=v.as_str().map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST",e))?; if !time::valid(s){return Err(malformed("MALFORMED_RESOLUTION_REQUEST","asOf must be RFC 3339"));} } }
    let opts = match o.get("options") { None => BTreeMap::new(), Some(Json::Object(m)) => m.clone(), Some(_) => return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "options must be object")) };
    for k in opts.keys() {
        if !["offline_only","max_bytes","max_results","allow_redirects","require_fresh","network_policy_id"].contains(&k.as_str()) { return Err(malformed("MALFORMED_RESOLUTION_REQUEST", "unknown resolution option")); }
    }
    let bool_opt = |key:&str, default:bool| -> Result<bool,OlpError> { match opts.get(key){None=>Ok(default),Some(v)=>v.as_bool().map_err(|e|malformed("MALFORMED_RESOLUTION_REQUEST",e))} };
    let uint_opt = |key:&str| -> Result<Option<u64>,OlpError> { match opts.get(key){None|Some(Json::Null)=>Ok(None),Some(v)=>Ok(Some(v.as_u64().map_err(|e|malformed("MALFORMED_RESOLUTION_REQUEST",e))?))} };
    if let Some(v)=opts.get("network_policy_id") { if !matches!(v,Json::Null) { let s=v.as_str().map_err(|e|malformed("MALFORMED_RESOLUTION_REQUEST",e))?; if !is_absolute_uri(s){return Err(malformed("MALFORMED_RESOLUTION_REQUEST","networkPolicyId must be absolute URI"));} } }
    Ok(Request { target_class, target, accept, offline_only: bool_opt("offline_only",false)?, max_bytes:uint_opt("max_bytes")?, max_results:uint_opt("max_results")?, allow_redirects:bool_opt("allow_redirects",false)?, require_fresh:bool_opt("require_fresh",false)? })
}

