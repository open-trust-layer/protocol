//! Independent Rust executable core for OLP Specifications 0006 and 0007.
//!
//! This module intentionally keeps principal identity, control, role, authority,
//! lifecycle evidence, and application policy as separate dimensions.  It never
//! emits a protocol-global trust score, current-state mutation, or authorization
//! boolean.

use std::collections::{BTreeMap, BTreeSet};

use crate::{
    error::OlpError,
    json::Json,
    record,
    time,
    util::{hex_decode, hex_encode, is_absolute_uri},
};

const PRINCIPAL_RELATION_DOMAIN: &str = "OLP-PRINCIPAL-RELATION";
const AUTHORITY_GRANT_DOMAIN: &str = "OLP-AUTHORITY-GRANT";
const AUTHORITY_STATUS_DOMAIN: &str = "OLP-AUTHORITY-STATUS";
const LIFECYCLE_STATUS_DOMAIN: &str = "OLP-LIFECYCLE-STATUS";

fn malformed(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::malformed(reason, message)
}

fn unsupported(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::unsupported(reason, message)
}

fn array<'a>(value: &'a Json, size: usize, reason: &str, label: &str) -> Result<&'a [Json], OlpError> {
    let items = value
        .as_array()
        .map_err(|_| malformed(reason, format!("{label} MUST be an array")))?;
    if items.len() != size {
        return Err(malformed(reason, format!("{label} MUST contain exactly {size} elements")));
    }
    Ok(items)
}

fn absolute_uri(value: &Json, reason: &str, label: &str) -> Result<String, OlpError> {
    let text = value
        .as_str()
        .map_err(|_| malformed(reason, format!("{label} MUST be an absolute URI")))?;
    if !is_absolute_uri(text) {
        return Err(malformed(reason, format!("{label} MUST be an absolute URI")));
    }
    Ok(text.to_string())
}

fn nullable_uri(value: &Json, reason: &str, label: &str) -> Result<Option<String>, OlpError> {
    match value {
        Json::Null => Ok(None),
        _ => absolute_uri(value, reason, label).map(Some),
    }
}

fn optional_time(value: &Json, reason: &str, label: &str) -> Result<Option<String>, OlpError> {
    match value {
        Json::Null => Ok(None),
        Json::String(text) if time::valid(text) => Ok(Some(text.clone())),
        _ => Err(malformed(reason, format!("{label} MUST be RFC 3339 or null"))),
    }
}

fn valid_abstract_value(value: &Json, depth: usize) -> bool {
    if depth > 64 {
        return false;
    }
    match value {
        Json::Null | Json::Bool(_) | Json::Int(_) | Json::String(_) => true,
        Json::Array(items) => items.len() <= 100_000 && items.iter().all(|v| valid_abstract_value(v, depth + 1)),
        Json::Object(map) if map.len() == 1 && map.contains_key("$bytes") => map
            .get("$bytes")
            .and_then(|v| v.as_str().ok())
            .is_some_and(|s| hex_decode(s).is_ok()),
        Json::Object(map) if map.len() == 1 && map.contains_key("$map") => map
            .get("$map")
            .and_then(|v| v.as_array().ok())
            .is_some_and(|entries| {
                entries.len() <= 100_000
                    && entries.iter().all(|entry| {
                        entry.as_array().ok().is_some_and(|pair| {
                            pair.len() == 2
                                && matches!(pair[0], Json::String(_) | Json::Int(_))
                                && valid_abstract_value(&pair[1], depth + 1)
                        })
                    })
            }),
        Json::Object(map) => map.len() <= 100_000 && map.values().all(|v| valid_abstract_value(v, depth + 1)),
    }
}

fn uri_map(value: &Json, reason: &str, label: &str) -> Result<BTreeMap<String, Json>, OlpError> {
    let map = value
        .as_object()
        .map_err(|_| malformed(reason, format!("{label} MUST be a map")))?;
    let mut result = BTreeMap::new();
    for (key, item) in map {
        if !is_absolute_uri(key) {
            return Err(malformed(reason, format!("{label} keys MUST be absolute URIs")));
        }
        if !valid_abstract_value(item, 0) {
            return Err(malformed(reason, format!("{label} contains an invalid OLP value")));
        }
        result.insert(key.clone(), item.clone());
    }
    Ok(result)
}

fn string_set_from_property(object: &BTreeMap<String, Json>, key: &str, reason: &str) -> Result<BTreeSet<String>, OlpError> {
    let Some(value) = object.get(key) else {
        return Ok(BTreeSet::new());
    };
    let items = value
        .as_array()
        .map_err(|_| malformed(reason, format!("{key} MUST be an array")))?;
    let mut result = BTreeSet::new();
    for item in items {
        let text = item
            .as_str()
            .map_err(|_| malformed(reason, format!("{key} members MUST be strings")))?;
        result.insert(text.to_string());
    }
    Ok(result)
}

fn critical(
    value: &Json,
    qualifiers: &BTreeMap<String, Json>,
    understood: &BTreeSet<String>,
    malformed_reason: &str,
    unsupported_reason: &str,
) -> Result<Vec<String>, OlpError> {
    let items = value
        .as_array()
        .map_err(|_| malformed(malformed_reason, "critical qualifiers MUST be an array"))?;
    let mut result = Vec::with_capacity(items.len());
    let mut seen = BTreeSet::new();
    for item in items {
        let text = item
            .as_str()
            .map_err(|_| malformed(malformed_reason, "critical qualifiers MUST contain text identifiers"))?;
        if !seen.insert(text.to_string()) {
            return Err(malformed(malformed_reason, "critical qualifiers MUST be unique"));
        }
        result.push(text.to_string());
    }
    let mut sorted = result.clone();
    sorted.sort_by(|a, b| a.as_bytes().cmp(b.as_bytes()));
    if result != sorted {
        return Err(malformed(malformed_reason, "critical qualifiers MUST be canonically sorted"));
    }
    for item in &result {
        if !is_absolute_uri(item) || !qualifiers.contains_key(item) {
            return Err(malformed(
                malformed_reason,
                "critical qualifier MUST name a present URI qualifier",
            ));
        }
        if !understood.contains(item) {
            return Err(unsupported(unsupported_reason, "unsupported critical qualifier"));
        }
    }
    Ok(result)
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct EvidenceRef {
    kind: i64,
    digest: [u8; 32],
}

fn wrapped_bytes32(value: &Json, reason: &str) -> Result<[u8; 32], OlpError> {
    let map = value
        .as_object()
        .map_err(|_| malformed(reason, "evidence digest MUST use the $bytes adapter projection"))?;
    if map.len() != 1 || !map.contains_key("$bytes") {
        return Err(malformed(reason, "evidence digest MUST use the $bytes adapter projection"));
    }
    let text = map["$bytes"]
        .as_str()
        .map_err(|_| malformed(reason, "$bytes MUST contain hexadecimal text"))?;
    let bytes = hex_decode(text).map_err(|_| malformed(reason, "evidence digest is not valid hexadecimal"))?;
    if bytes.len() != 32 {
        return Err(malformed(reason, "EvidenceRefV1 digest MUST contain exactly 32 octets"));
    }
    let mut digest = [0u8; 32];
    digest.copy_from_slice(&bytes);
    Ok(digest)
}

fn evidence_ref(value: &Json, required_kind: Option<i64>, reason: &str) -> Result<EvidenceRef, OlpError> {
    let raw = array(value, 2, reason, "EvidenceRefV1")?;
    let kind = raw[0]
        .as_i64()
        .map_err(|_| malformed(reason, "EvidenceRefV1 kind MUST be integer 0 or 1"))?;
    if kind != 0 && kind != 1 {
        return Err(malformed(reason, "EvidenceRefV1 kind MUST be 0 or 1"));
    }
    if required_kind.is_some_and(|required| required != kind) {
        return Err(malformed(reason, "EvidenceRefV1 kind does not match target category"));
    }
    Ok(EvidenceRef {
        kind,
        digest: wrapped_bytes32(&raw[1], reason)?,
    })
}

fn evidence_ref_json(value: &EvidenceRef) -> Json {
    Json::Array(vec![
        Json::Int(value.kind as i128),
        Json::String(hex_encode(&value.digest)),
    ])
}

fn json_strings(values: &[String]) -> Json {
    Json::Array(values.iter().cloned().map(Json::String).collect())
}

fn opt_string(value: &Option<String>) -> Json {
    value.clone().map(Json::String).unwrap_or(Json::Null)
}

fn principal_relation(input: &Json, understood: &BTreeSet<String>) -> Result<Json, OlpError> {
    let raw = array(input, 8, "MALFORMED_PRINCIPAL_RELATION", "PrincipalRelationStatementV1")?;
    if raw[0].as_str().ok() != Some(PRINCIPAL_RELATION_DOMAIN) {
        return Err(malformed("MALFORMED_PRINCIPAL_RELATION", "invalid principal relation discriminator"));
    }
    let version = raw[1]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_PRINCIPAL_RELATION", "principal relation version MUST be integer"))?;
    if version != 1 {
        return Err(unsupported(
            "UNSUPPORTED_PRINCIPAL_RELATION_VERSION",
            "unsupported principal relation version",
        ));
    }
    let relation = raw[2]
        .as_str()
        .map_err(|_| malformed("MALFORMED_PRINCIPAL_RELATION", "relation type MUST be non-empty text"))?;
    if relation.is_empty() {
        return Err(malformed("MALFORMED_PRINCIPAL_RELATION", "relation type MUST be non-empty text"));
    }
    let relation_is_core = matches!(
        relation,
        "controlsVerificationMethod" | "sameSubjectAs" | "memberOf" | "holdsRole"
    );
    if !relation_is_core {
        if !is_absolute_uri(relation) {
            return Err(malformed("MALFORMED_PRINCIPAL_RELATION", "unknown compact principal relation"));
        }
        return Err(unsupported(
            "UNSUPPORTED_PRINCIPAL_RELATION_TYPE",
            "unsupported principal relation type",
        ));
    }
    let subject = absolute_uri(&raw[3], "MALFORMED_PRINCIPAL_RELATION", "principal relation subject")?;
    let object_raw = array(&raw[4], 2, "MALFORMED_PRINCIPAL_RELATION", "PrincipalObjectRefV1")?;
    let object_kind = object_raw[0]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_PRINCIPAL_RELATION", "principal object kind MUST be an integer"))?;
    if !(0..=2).contains(&object_kind) {
        return Err(unsupported(
            "UNSUPPORTED_PRINCIPAL_OBJECT_KIND",
            "unsupported principal object kind",
        ));
    }
    let object_identifier = absolute_uri(
        &object_raw[1],
        "MALFORMED_PRINCIPAL_RELATION",
        "principal object identifier",
    )?;
    let context = nullable_uri(&raw[5], "MALFORMED_PRINCIPAL_RELATION", "principal relation context")?;
    let qualifiers = uri_map(&raw[6], "MALFORMED_PRINCIPAL_RELATION", "principal relation qualifiers")?;
    let crit = critical(
        &raw[7],
        &qualifiers,
        understood,
        "MALFORMED_PRINCIPAL_RELATION",
        "UNSUPPORTED_CRITICAL_PRINCIPAL_QUALIFIER",
    )?;

    let expected_kind = match relation {
        "controlsVerificationMethod" => 1,
        "sameSubjectAs" | "memberOf" => 0,
        "holdsRole" => 2,
        _ => unreachable!(),
    };
    if object_kind != expected_kind {
        return Err(malformed(
            "INVALID_PRINCIPAL_RELATION_OBJECT",
            "principal relation object kind is invalid for relation type",
        ));
    }
    if relation == "holdsRole" {
        if context.is_none() {
            return Err(malformed(
                "INVALID_PRINCIPAL_RELATION_CONTEXT",
                "holdsRole requires context",
            ));
        }
    } else if context.is_some() {
        return Err(malformed(
            "INVALID_PRINCIPAL_RELATION_CONTEXT",
            "core principal relation forbids context",
        ));
    }

    let mut uninterpreted: Vec<String> = qualifiers
        .keys()
        .filter(|key| !understood.contains(*key))
        .cloned()
        .collect();
    uninterpreted.sort_by(|a, b| a.as_bytes().cmp(b.as_bytes()));

    let mut out = Json::object();
    out.insert("kind".into(), Json::String("principal_relation".into()));
    out.insert("relation_type".into(), Json::String(relation.into()));
    out.insert("subject".into(), Json::String(subject));
    out.insert("object_kind".into(), Json::Int(object_kind as i128));
    out.insert("object_identifier".into(), Json::String(object_identifier));
    out.insert("context".into(), opt_string(&context));
    out.insert("critical".into(), json_strings(&crit));
    out.insert("uninterpreted_qualifiers".into(), json_strings(&uninterpreted));
    out.insert("trust".into(), Json::String("NOT_EVALUATED".into()));
    out.insert("authority".into(), Json::String("NOT_EVALUATED".into()));
    Ok(Json::Object(out))
}

#[derive(Clone, Debug, PartialEq, Eq)]
enum AuthorityResource {
    Uri(String),
    Evidence(EvidenceRef),
}

#[derive(Clone, Debug)]
struct Grant {
    grantor: String,
    grantee: String,
    action: String,
    resource: Option<AuthorityResource>,
    context: Option<String>,
    valid_from: Option<String>,
    valid_until: Option<String>,
    delegable: bool,
    parent_grant: Option<EvidenceRef>,
    constraints: BTreeMap<String, Json>,
    #[allow(dead_code)]
    extensions: BTreeMap<String, Json>,
}

fn authority_resource(value: &Json) -> Result<Option<AuthorityResource>, OlpError> {
    if matches!(value, Json::Null) {
        return Ok(None);
    }
    let raw = array(value, 2, "MALFORMED_AUTHORITY_GRANT", "AuthorityResourceRefV1")?;
    let kind = raw[0]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_AUTHORITY_GRANT", "authority resource kind MUST be integer"))?;
    match kind {
        0 => Ok(Some(AuthorityResource::Uri(absolute_uri(
            &raw[1],
            "MALFORMED_AUTHORITY_GRANT",
            "authority resource URI",
        )?))),
        1 => Ok(Some(AuthorityResource::Evidence(evidence_ref(
            &raw[1],
            None,
            "MALFORMED_AUTHORITY_GRANT",
        )?))),
        _ => Err(unsupported(
            "UNSUPPORTED_AUTHORITY_RESOURCE_KIND",
            "unsupported authority resource kind",
        )),
    }
}

fn authority_resource_json(value: &Option<AuthorityResource>) -> Json {
    match value {
        None => Json::Null,
        Some(AuthorityResource::Uri(uri)) => Json::Array(vec![Json::Int(0), Json::String(uri.clone())]),
        Some(AuthorityResource::Evidence(reference)) => {
            Json::Array(vec![Json::Int(1), evidence_ref_json(reference)])
        }
    }
}

fn authority_grant(value: &Json, understood_constraints: &BTreeSet<String>) -> Result<Grant, OlpError> {
    let raw = array(value, 13, "MALFORMED_AUTHORITY_GRANT", "AuthorityGrantStatementV1")?;
    if raw[0].as_str().ok() != Some(AUTHORITY_GRANT_DOMAIN) {
        return Err(malformed("MALFORMED_AUTHORITY_GRANT", "invalid authority grant discriminator"));
    }
    let version = raw[1]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_AUTHORITY_GRANT", "authority grant version MUST be integer"))?;
    if version != 1 {
        return Err(unsupported(
            "UNSUPPORTED_AUTHORITY_GRANT_VERSION",
            "unsupported authority grant version",
        ));
    }
    let grantor = absolute_uri(&raw[2], "MALFORMED_AUTHORITY_GRANT", "grantor")?;
    let grantee = absolute_uri(&raw[3], "MALFORMED_AUTHORITY_GRANT", "grantee")?;
    let action = absolute_uri(&raw[4], "MALFORMED_AUTHORITY_GRANT", "action")?;
    let resource = authority_resource(&raw[5])?;
    let context = nullable_uri(&raw[6], "MALFORMED_AUTHORITY_GRANT", "authority context")?;
    let valid_from = optional_time(&raw[7], "MALFORMED_AUTHORITY_GRANT", "validFrom")?;
    let valid_until = optional_time(&raw[8], "MALFORMED_AUTHORITY_GRANT", "validUntil")?;
    if let (Some(lower), Some(upper)) = (&valid_from, &valid_until) {
        if time::parse(lower).unwrap() >= time::parse(upper).unwrap() {
            return Err(malformed(
                "INVALID_AUTHORITY_INTERVAL",
                "validFrom MUST be earlier than validUntil",
            ));
        }
    }
    let delegable = raw[9]
        .as_bool()
        .map_err(|_| malformed("MALFORMED_AUTHORITY_GRANT", "delegable MUST be boolean"))?;
    let parent_grant = match &raw[10] {
        Json::Null => None,
        other => Some(evidence_ref(other, Some(0), "MALFORMED_AUTHORITY_GRANT")?),
    };
    let constraints = uri_map(&raw[11], "MALFORMED_AUTHORITY_GRANT", "authority constraints")?;
    if constraints.keys().any(|key| !understood_constraints.contains(key)) {
        return Err(unsupported(
            "UNSUPPORTED_AUTHORITY_CONSTRAINT",
            "unsupported authority constraint",
        ));
    }
    let extensions = uri_map(&raw[12], "MALFORMED_AUTHORITY_GRANT", "authority extensions")?;
    Ok(Grant {
        grantor,
        grantee,
        action,
        resource,
        context,
        valid_from,
        valid_until,
        delegable,
        parent_grant,
        constraints,
        extensions,
    })
}

fn interval(grant: &Grant, evaluation_time: Option<&Json>) -> Result<String, OlpError> {
    let Some(value) = evaluation_time else {
        return Ok("NOT_EVALUATED".into());
    };
    let text = value
        .as_str()
        .map_err(|_| malformed("MALFORMED_EVALUATION_CONTEXT", "evaluation_time MUST be RFC 3339"))?;
    let now = time::parse(text)
        .ok_or_else(|| malformed("MALFORMED_EVALUATION_CONTEXT", "evaluation_time MUST be RFC 3339"))?;
    let lower = grant.valid_from.as_deref().and_then(time::parse);
    let upper = grant.valid_until.as_deref().and_then(time::parse);
    if lower.is_none() && upper.is_none() {
        return Ok("NO_DECLARED_BOUND".into());
    }
    if lower.is_some_and(|value| now < value) {
        return Ok("BEFORE_DECLARED_INTERVAL".into());
    }
    if upper.is_some_and(|value| now >= value) {
        return Ok("AFTER_DECLARED_INTERVAL".into());
    }
    Ok("WITHIN_DECLARED_INTERVAL".into())
}

fn grant_output(grant: &Grant, evaluation_time: Option<&Json>) -> Result<Json, OlpError> {
    let mut out = Json::object();
    out.insert("kind".into(), Json::String("authority_grant".into()));
    out.insert("grantor".into(), Json::String(grant.grantor.clone()));
    out.insert("grantee".into(), Json::String(grant.grantee.clone()));
    out.insert("action".into(), Json::String(grant.action.clone()));
    out.insert("resource".into(), authority_resource_json(&grant.resource));
    out.insert("context".into(), opt_string(&grant.context));
    out.insert("delegable".into(), Json::Bool(grant.delegable));
    out.insert(
        "parent_grant".into(),
        grant
            .parent_grant
            .as_ref()
            .map(evidence_ref_json)
            .unwrap_or(Json::Null),
    );
    out.insert("temporal_applicability".into(), Json::String(interval(grant, evaluation_time)?));
    out.insert("grant_attribution".into(), Json::String("NOT_EVALUATED".into()));
    out.insert("status".into(), Json::String("NOT_EVALUATED".into()));
    out.insert("policy_decision".into(), Json::String("NOT_EVALUATED".into()));
    Ok(Json::Object(out))
}

fn interval_within(parent: &Grant, child: &Grant) -> bool {
    let p_from = parent.valid_from.as_deref().and_then(time::parse);
    let p_until = parent.valid_until.as_deref().and_then(time::parse);
    let c_from = child.valid_from.as_deref().and_then(time::parse);
    let c_until = child.valid_until.as_deref().and_then(time::parse);
    if let Some(lower) = p_from {
        if c_from.is_none_or(|child_lower| child_lower < lower) {
            return false;
        }
    }
    if let Some(upper) = p_until {
        if c_until.is_none_or(|child_upper| child_upper > upper) {
            return false;
        }
    }
    true
}

fn delegation(payload: &BTreeMap<String, Json>, understood: &BTreeSet<String>) -> Result<Json, OlpError> {
    let child = authority_grant(
        payload
            .get("child")
            .ok_or_else(|| malformed("MALFORMED_DELEGATION_INPUT", "missing child grant"))?,
        understood,
    )?;
    let Some(claimed_parent) = child.parent_grant.clone() else {
        let mut out = Json::object();
        out.insert("kind".into(), Json::String("delegation".into()));
        out.insert("delegation_status".into(), Json::String("NO_PARENT_CLAIMED".into()));
        out.insert("reasons".into(), Json::Array(vec![]));
        out.insert("scope".into(), Json::String("NOT_EVALUATED".into()));
        out.insert("parent_identity".into(), Json::String("NOT_APPLICABLE".into()));
        out.insert("policy_decision".into(), Json::String("NOT_EVALUATED".into()));
        return Ok(Json::Object(out));
    };
    let Some(parent_record) = payload.get("parent_record") else {
        let mut out = Json::object();
        out.insert("kind".into(), Json::String("delegation".into()));
        out.insert("delegation_status".into(), Json::String("UNRESOLVED_PARENT".into()));
        out.insert("reasons".into(), json_strings(&["PARENT_GRANT_UNRESOLVED".into()]));
        out.insert("scope".into(), Json::String("INDETERMINATE".into()));
        out.insert("parent_identity".into(), Json::String("UNRESOLVED".into()));
        out.insert("policy_decision".into(), Json::String("NOT_EVALUATED".into()));
        return Ok(Json::Object(out));
    };

    let digest = record::identity_digest(parent_record)?;
    let computed = EvidenceRef { kind: 0, digest };
    if computed != claimed_parent {
        let mut out = Json::object();
        out.insert("kind".into(), Json::String("delegation".into()));
        out.insert("delegation_status".into(), Json::String("UNRESOLVED_PARENT".into()));
        out.insert("reasons".into(), json_strings(&["PARENT_GRANT_IDENTITY_MISMATCH".into()]));
        out.insert("scope".into(), Json::String("INDETERMINATE".into()));
        out.insert("parent_identity".into(), Json::String("MISMATCH".into()));
        out.insert("computed_parent_reference".into(), evidence_ref_json(&computed));
        out.insert("policy_decision".into(), Json::String("NOT_EVALUATED".into()));
        return Ok(Json::Object(out));
    }

    let parent_content = parent_record
        .get("content")
        .map_err(|_| malformed("PARENT_GRANT_TYPE_MISMATCH", "parent record has no authority-grant content"))?;
    let parent = authority_grant(parent_content, understood).map_err(|_| {
        malformed(
            "PARENT_GRANT_TYPE_MISMATCH",
            "referenced parent record is not a supported AuthorityGrantStatementV1",
        )
    })?;

    let mut reasons = Vec::<String>::new();
    let mut exact_scope = true;
    if parent.grantee != child.grantor {
        reasons.push("DELEGATION_PRINCIPAL_MISMATCH".into());
    }
    if !parent.delegable {
        reasons.push("PARENT_GRANT_NOT_DELEGABLE".into());
    }
    if parent.action != child.action {
        reasons.push("DELEGATION_ACTION_SCOPE_MISMATCH".into());
        exact_scope = false;
    }
    if parent.resource != child.resource {
        reasons.push("DELEGATION_RESOURCE_SCOPE_MISMATCH".into());
        exact_scope = false;
    }
    if parent.context != child.context {
        reasons.push("DELEGATION_CONTEXT_SCOPE_MISMATCH".into());
        exact_scope = false;
    }
    if !interval_within(&parent, &child) {
        reasons.push("DELEGATION_TIME_SCOPE_MISMATCH".into());
        exact_scope = false;
    }
    if parent.constraints != child.constraints {
        reasons.push("DELEGATION_CONSTRAINT_SCOPE_INDETERMINATE".into());
        exact_scope = false;
    }

    let mut out = Json::object();
    out.insert("kind".into(), Json::String("delegation".into()));
    out.insert(
        "delegation_status".into(),
        Json::String(if reasons.is_empty() { "SUPPORTED" } else { "NOT_SUPPORTED" }.into()),
    );
    out.insert("reasons".into(), json_strings(&reasons));
    out.insert(
        "scope".into(),
        Json::String(if exact_scope {
            "WITHIN_PARENT_EXACT_BASELINE"
        } else {
            "OUTSIDE_OR_INDETERMINATE"
        }
        .into()),
    );
    out.insert("parent_identity".into(), Json::String("VERIFIED".into()));
    out.insert("parent_reference".into(), evidence_ref_json(&computed));
    out.insert("policy_decision".into(), Json::String("NOT_EVALUATED".into()));
    Ok(Json::Object(out))
}

fn authority_status(value: &Json, understood: &BTreeSet<String>) -> Result<Json, OlpError> {
    let raw = array(value, 8, "MALFORMED_AUTHORITY_STATUS", "AuthorityStatusStatementV1")?;
    if raw[0].as_str().ok() != Some(AUTHORITY_STATUS_DOMAIN) {
        return Err(malformed("MALFORMED_AUTHORITY_STATUS", "invalid authority status discriminator"));
    }
    let version = raw[1]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_AUTHORITY_STATUS", "authority status version MUST be integer"))?;
    if version != 1 {
        return Err(unsupported(
            "UNSUPPORTED_AUTHORITY_STATUS_VERSION",
            "unsupported authority status version",
        ));
    }
    let target = evidence_ref(&raw[2], Some(0), "MALFORMED_AUTHORITY_STATUS")?;
    let event = raw[3]
        .as_str()
        .map_err(|_| malformed("MALFORMED_AUTHORITY_STATUS", "authority status event MUST be text"))?;
    if event.is_empty() {
        return Err(malformed("MALFORMED_AUTHORITY_STATUS", "authority status event MUST be text"));
    }
    if !matches!(event, "suspend" | "resume" | "revoke") {
        if !is_absolute_uri(event) {
            return Err(malformed("MALFORMED_AUTHORITY_STATUS", "unknown compact authority status event"));
        }
        return Err(unsupported(
            "UNSUPPORTED_AUTHORITY_STATUS_EVENT",
            "unsupported authority status event",
        ));
    }
    let effective_at = optional_time(&raw[4], "MALFORMED_AUTHORITY_STATUS", "effectiveAt")?;
    let reason = nullable_uri(&raw[5], "MALFORMED_AUTHORITY_STATUS", "authority status reason")?;
    let qualifiers = uri_map(&raw[6], "MALFORMED_AUTHORITY_STATUS", "authority status qualifiers")?;
    let crit = critical(
        &raw[7],
        &qualifiers,
        understood,
        "MALFORMED_AUTHORITY_STATUS",
        "UNSUPPORTED_CRITICAL_AUTHORITY_STATUS_QUALIFIER",
    )?;

    let mut out = Json::object();
    out.insert("kind".into(), Json::String("authority_status".into()));
    out.insert("target_grant".into(), evidence_ref_json(&target));
    out.insert("event".into(), Json::String(event.into()));
    out.insert("effective_at".into(), opt_string(&effective_at));
    out.insert("reason".into(), opt_string(&reason));
    out.insert("critical".into(), json_strings(&crit));
    out.insert("producer_authority".into(), Json::String("NOT_EVALUATED".into()));
    out.insert("mutates_target".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
enum LifecycleTarget {
    Evidence(String, EvidenceRef),
    Uri(String, String),
}

fn lifecycle_target(value: &Json) -> Result<LifecycleTarget, OlpError> {
    let raw = array(value, 2, "MALFORMED_LIFECYCLE_TARGET", "LifecycleTargetV1")?;
    let target_type = raw[0]
        .as_str()
        .map_err(|_| malformed("MALFORMED_LIFECYCLE_TARGET", "lifecycle target type MUST be text"))?;
    if target_type.is_empty() {
        return Err(malformed("MALFORMED_LIFECYCLE_TARGET", "lifecycle target type MUST be text"));
    }
    match target_type {
        "record" => Ok(LifecycleTarget::Evidence(
            target_type.into(),
            evidence_ref(&raw[1], Some(0), "MALFORMED_LIFECYCLE_TARGET")?,
        )),
        "proof" => Ok(LifecycleTarget::Evidence(
            target_type.into(),
            evidence_ref(&raw[1], Some(1), "MALFORMED_LIFECYCLE_TARGET")?,
        )),
        "verificationMethod" | "principal" => Ok(LifecycleTarget::Uri(
            target_type.into(),
            absolute_uri(&raw[1], "MALFORMED_LIFECYCLE_TARGET", "lifecycle target identifier")?,
        )),
        other if is_absolute_uri(other) => Err(unsupported(
            "UNSUPPORTED_LIFECYCLE_TARGET_TYPE",
            "unsupported lifecycle target type",
        )),
        _ => Err(malformed(
            "MALFORMED_LIFECYCLE_TARGET",
            "unknown compact lifecycle target type",
        )),
    }
}

fn lifecycle_target_json(target: &LifecycleTarget) -> Json {
    match target {
        LifecycleTarget::Evidence(kind, reference) => {
            Json::Array(vec![Json::String(kind.clone()), evidence_ref_json(reference)])
        }
        LifecycleTarget::Uri(kind, identifier) => {
            Json::Array(vec![Json::String(kind.clone()), Json::String(identifier.clone())])
        }
    }
}

#[derive(Clone, Debug)]
struct LifecycleStatus {
    target: LifecycleTarget,
    event: String,
    status_authority: Option<String>,
    effective_at: Option<String>,
    sequence: Option<u64>,
    scope: Option<String>,
    next_update: Option<String>,
    #[allow(dead_code)]
    reason: Option<String>,
    #[allow(dead_code)]
    critical: Vec<String>,
}

fn lifecycle_status(value: &Json, understood: &BTreeSet<String>) -> Result<LifecycleStatus, OlpError> {
    let raw = array(value, 12, "MALFORMED_LIFECYCLE_STATUS", "LifecycleStatusStatementV1")?;
    if raw[0].as_str().ok() != Some(LIFECYCLE_STATUS_DOMAIN) {
        return Err(malformed("MALFORMED_LIFECYCLE_STATUS", "invalid lifecycle status discriminator"));
    }
    let version = raw[1]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_LIFECYCLE_STATUS", "lifecycle status version MUST be integer"))?;
    if version != 1 {
        return Err(unsupported(
            "UNSUPPORTED_LIFECYCLE_STATUS_VERSION",
            "unsupported lifecycle status version",
        ));
    }
    let target = lifecycle_target(&raw[2])?;
    let event = raw[3]
        .as_str()
        .map_err(|_| malformed("MALFORMED_LIFECYCLE_STATUS", "lifecycle event MUST be text"))?;
    if event.is_empty() {
        return Err(malformed("MALFORMED_LIFECYCLE_STATUS", "lifecycle event MUST be text"));
    }
    if !matches!(
        event,
        "activate" | "suspend" | "resume" | "retire" | "revoke" | "compromise" | "deprecate"
    ) {
        if !is_absolute_uri(event) {
            return Err(malformed("MALFORMED_LIFECYCLE_STATUS", "unknown compact lifecycle event"));
        }
        return Err(unsupported(
            "UNSUPPORTED_LIFECYCLE_EVENT",
            "unsupported lifecycle event",
        ));
    }
    let status_authority = nullable_uri(&raw[4], "MALFORMED_LIFECYCLE_STATUS", "statusAuthority")?;
    let effective_at = optional_time(&raw[5], "MALFORMED_LIFECYCLE_STATUS", "effectiveAt")?;
    let sequence = match &raw[6] {
        Json::Null => None,
        other => Some(
            other
                .as_u64()
                .map_err(|_| malformed("MALFORMED_LIFECYCLE_STATUS", "sequence MUST be non-negative integer or null"))?,
        ),
    };
    if sequence.is_some() && status_authority.is_none() {
        return Err(malformed(
            "MALFORMED_LIFECYCLE_STATUS",
            "sequence requires statusAuthority",
        ));
    }
    let scope = nullable_uri(&raw[7], "MALFORMED_LIFECYCLE_STATUS", "scope")?;
    let next_update = optional_time(&raw[8], "MALFORMED_LIFECYCLE_STATUS", "nextUpdate")?;
    let reason = nullable_uri(&raw[9], "MALFORMED_LIFECYCLE_STATUS", "reason")?;
    let qualifiers = uri_map(&raw[10], "MALFORMED_LIFECYCLE_STATUS", "lifecycle qualifiers")?;
    let crit = critical(
        &raw[11],
        &qualifiers,
        understood,
        "MALFORMED_LIFECYCLE_STATUS",
        "UNSUPPORTED_CRITICAL_LIFECYCLE_QUALIFIER",
    )?;
    Ok(LifecycleStatus {
        target,
        event: event.into(),
        status_authority,
        effective_at,
        sequence,
        scope,
        next_update,
        reason,
        critical: crit,
    })
}

fn lifecycle(payload: &BTreeMap<String, Json>, understood: &BTreeSet<String>) -> Result<Json, OlpError> {
    let target = lifecycle_target(
        payload
            .get("target")
            .ok_or_else(|| malformed("MALFORMED_LIFECYCLE_INPUT", "missing lifecycle target"))?,
    )?;
    let empty_statuses = Json::Array(vec![]);
    let statuses_value = payload.get("statuses").unwrap_or(&empty_statuses);
    let statuses = statuses_value
        .as_array()
        .map_err(|_| malformed("MALFORMED_LIFECYCLE_INPUT", "statuses MUST be an array"))?;
    if statuses.len() > 64 {
        return Err(malformed(
            "RESOURCE_LIMIT_EXCEEDED",
            "lifecycle evidence exceeds implementation limit",
        ));
    }
    let evaluation = match payload.get("evaluation_time") {
        None | Some(Json::Null) => None,
        Some(Json::String(text)) => Some(
            time::parse(text)
                .ok_or_else(|| malformed("MALFORMED_EVALUATION_CONTEXT", "evaluation_time MUST be RFC 3339"))?,
        ),
        Some(_) => {
            return Err(malformed(
                "MALFORMED_EVALUATION_CONTEXT",
                "evaluation_time MUST be RFC 3339",
            ))
        }
    };
    let required_scope = match payload.get("required_scope") {
        None | Some(Json::Null) => None,
        Some(value) => Some(absolute_uri(
            value,
            "MALFORMED_EVALUATION_CONTEXT",
            "required_scope",
        )?),
    };

    #[derive(Clone)]
    struct Accepted {
        event: String,
        status_authority: Option<String>,
        sequence: Option<u64>,
        scope: Option<String>,
        effective: String,
        freshness: String,
    }

    let mut accepted = Vec::<Accepted>::new();
    let mut event_outputs = Vec::<Json>::new();
    for (index, raw) in statuses.iter().enumerate() {
        let status = lifecycle_status(raw, understood)?;
        if status.target != target {
            continue;
        }
        if required_scope.as_ref().is_some_and(|scope| status.scope.as_ref() != Some(scope)) {
            continue;
        }
        let effective = match (&status.effective_at, evaluation) {
            (None, _) => "NO_DECLARED_TIME".to_string(),
            (Some(_), None) => "NOT_EVALUATED".to_string(),
            (Some(value), Some(now)) => {
                if time::parse(value).unwrap() <= now {
                    "EFFECTIVE".into()
                } else {
                    "STATUS_EVENT_NOT_YET_EFFECTIVE".into()
                }
            }
        };
        let freshness = match (&status.next_update, evaluation) {
            (Some(value), Some(now)) if now > time::parse(value).unwrap() => "STALE_BY_SOURCE".to_string(),
            (Some(_), Some(_)) => "WITHIN_SOURCE_WINDOW".to_string(),
            _ => "NOT_EVALUATED".to_string(),
        };
        let item = Accepted {
            event: status.event.clone(),
            status_authority: status.status_authority.clone(),
            sequence: status.sequence,
            scope: status.scope.clone(),
            effective: effective.clone(),
            freshness: freshness.clone(),
        };
        let mut output = Json::object();
        output.insert("index".into(), Json::Int(index as i128));
        output.insert("event".into(), Json::String(status.event));
        output.insert("status_authority".into(), opt_string(&status.status_authority));
        output.insert(
            "sequence".into(),
            status.sequence.map(|v| Json::Int(v as i128)).unwrap_or(Json::Null),
        );
        output.insert("scope".into(), opt_string(&status.scope));
        output.insert("effective".into(), Json::String(effective));
        output.insert("freshness".into(), Json::String(freshness));
        event_outputs.push(Json::Object(output));
        accepted.push(item);
    }

    let mut conflicts = Vec::<String>::new();
    let mut seen: BTreeMap<(Option<String>, LifecycleTarget, Option<String>, u64), (String, String, String)> =
        BTreeMap::new();
    for status in &accepted {
        let Some(sequence) = status.sequence else {
            continue;
        };
        let key = (
            status.status_authority.clone(),
            target.clone(),
            status.scope.clone(),
            sequence,
        );
        let material = (
            status.event.clone(),
            status.effective.clone(),
            status.freshness.clone(),
        );
        if let Some(previous) = seen.get(&key) {
            if previous != &material && conflicts.is_empty() {
                conflicts.push("STATUS_SEQUENCE_CONFLICT".into());
            }
        } else {
            seen.insert(key, material);
        }
    }

    let freshness = if accepted.iter().any(|item| item.freshness == "STALE_BY_SOURCE") {
        "STALE"
    } else if accepted.iter().any(|item| item.freshness == "WITHIN_SOURCE_WINDOW") {
        "FRESHNESS_SIGNAL_PRESENT"
    } else {
        "NOT_EVALUATED"
    };

    let mut out = Json::object();
    out.insert("kind".into(), Json::String("lifecycle".into()));
    out.insert("target".into(), lifecycle_target_json(&target));
    out.insert("events".into(), Json::Array(event_outputs));
    out.insert("conflicts".into(), json_strings(&conflicts));
    out.insert("freshness".into(), Json::String(freshness.into()));
    out.insert("completeness".into(), Json::String("UNKNOWN".into()));
    out.insert("source_authority".into(), Json::String("NOT_EVALUATED".into()));
    out.insert("operational_state".into(), Json::String("INDETERMINATE".into()));
    out.insert("absence_is_active".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

pub fn evaluate_operation(input: &Json) -> Result<Json, OlpError> {
    let payload = input
        .as_object()
        .map_err(|_| malformed("MALFORMED_INPUT", "input MUST be a map"))?;
    let mode = payload
        .get("mode")
        .and_then(|value| value.as_str().ok())
        .ok_or_else(|| unsupported("UNSUPPORTED_AUTHORITY_LIFECYCLE_MODE", "unsupported M21 operation mode"))?;
    match mode {
        "principal_relation" => {
            let understood = string_set_from_property(
                payload,
                "understood_critical_qualifiers",
                "MALFORMED_PRINCIPAL_RELATION",
            )?;
            principal_relation(
                payload
                    .get("statement")
                    .ok_or_else(|| malformed("MALFORMED_PRINCIPAL_RELATION", "missing statement"))?,
                &understood,
            )
        }
        "authority_grant" => {
            let understood = string_set_from_property(
                payload,
                "understood_constraints",
                "MALFORMED_AUTHORITY_GRANT",
            )?;
            let grant = authority_grant(
                payload
                    .get("statement")
                    .ok_or_else(|| malformed("MALFORMED_AUTHORITY_GRANT", "missing statement"))?,
                &understood,
            )?;
            grant_output(&grant, payload.get("evaluation_time"))
        }
        "delegation" => {
            let understood = string_set_from_property(
                payload,
                "understood_constraints",
                "MALFORMED_DELEGATION_INPUT",
            )?;
            delegation(payload, &understood)
        }
        "authority_status" => {
            let understood = string_set_from_property(
                payload,
                "understood_critical_qualifiers",
                "MALFORMED_AUTHORITY_STATUS",
            )?;
            authority_status(
                payload
                    .get("statement")
                    .ok_or_else(|| malformed("MALFORMED_AUTHORITY_STATUS", "missing statement"))?,
                &understood,
            )
        }
        "lifecycle" => {
            let understood = string_set_from_property(
                payload,
                "understood_critical_qualifiers",
                "MALFORMED_LIFECYCLE_INPUT",
            )?;
            lifecycle(payload, &understood)
        }
        _ => Err(unsupported(
            "UNSUPPORTED_AUTHORITY_LIFECYCLE_MODE",
            "unsupported M21 operation mode",
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn absence_never_implies_active() {
        let input = crate::json::parse(
            r#"{"mode":"lifecycle","target":["principal","did:example:alice"],"statuses":[]}"#,
        )
        .unwrap();
        let result = evaluate_operation(&input).unwrap();
        assert_eq!(result.get("operational_state").unwrap().as_str().unwrap(), "INDETERMINATE");
        assert!(!result.get("absence_is_active").unwrap().as_bool().unwrap());
    }

    #[test]
    fn role_does_not_become_authority() {
        let input = crate::json::parse(
            r#"{"mode":"principal_relation","statement":["OLP-PRINCIPAL-RELATION",1,"holdsRole","did:example:alice",[2,"urn:example:role:auditor"],"did:example:org:acme",{},[]]}"#,
        )
        .unwrap();
        let result = evaluate_operation(&input).unwrap();
        assert_eq!(result.get("authority").unwrap().as_str().unwrap(), "NOT_EVALUATED");
        assert!(result.get_opt("authorized").unwrap().is_none());
    }
}
