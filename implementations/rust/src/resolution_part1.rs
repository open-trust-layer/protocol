// Specification 0009 deterministic, offline-first resolution core.
//
// This module consumes caller-supplied resolver snapshots. It performs no network I/O.

use std::collections::{BTreeMap, BTreeSet};
use std::net::{IpAddr, Ipv6Addr};

use crate::{
    error::OlpError,
    json::Json,
    proof_identity,
    record,
    sha256,
    time,
    util::{hex_decode, hex_encode, is_absolute_uri},
};

const DOMAIN: &str = "OLP-RESOLUTION-REQUEST";
const CORE_TARGETS: [&str; 6] = [
    "evidence",
    "verificationMethod",
    "principal",
    "externalResource",
    "lifecycle",
    "service",
];

#[derive(Clone, Debug, PartialEq, Eq)]
struct EvidenceRef {
    kind: i64,
    digest: [u8; 32],
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ResourceRef {
    resource_id: Option<String>,
    media_type: String,
    algorithm: i64,
    digest: [u8; 32],
}

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

fn malformed(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::malformed(reason, message)
}

fn parse_evidence_ref(v: &Json) -> Result<EvidenceRef, OlpError> {
    let m = v
        .as_object()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let kind = m
        .get("kind")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "kind required"))?
        .as_i64()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    if kind != 0 && kind != 1 {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "invalid evidence kind",
        ));
    }
    let digest_hex = m
        .get("identity_digest_hex")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "digest required"))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let raw = hex_decode(digest_hex)
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    if raw.len() != 32 {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "evidence digest must be 32 bytes",
        ));
    }
    let mut digest = [0u8; 32];
    digest.copy_from_slice(&raw);
    Ok(EvidenceRef { kind, digest })
}

fn ref_json(r: &EvidenceRef) -> Json {
    Json::Object(BTreeMap::from([
        (
            "identity_digest_hex".into(),
            Json::String(hex_encode(&r.digest)),
        ),
        ("kind".into(), Json::Int(r.kind as i128)),
    ]))
}

fn parse_resource_ref(v: &Json) -> Result<ResourceRef, OlpError> {
    let m = v
        .as_object()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let resource_id = match m.get("resource_id") {
        None | Some(Json::Null) => None,
        Some(Json::String(value)) => {
            if !is_absolute_uri(value) {
                return Err(malformed(
                    "MALFORMED_RESOLUTION_REQUEST",
                    "resource_id must be an absolute URI or null",
                ));
            }
            Some(value.clone())
        }
        Some(_) => {
            return Err(malformed(
                "MALFORMED_RESOLUTION_REQUEST",
                "resource_id must be text or null",
            ))
        }
    };
    let media_type = m
        .get("media_type")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "media_type required"))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?
        .to_string();
    if media_type.is_empty() {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "media_type must be non-empty text",
        ));
    }
    let algorithm = match m.get("hash_algorithm") {
        None => -16,
        Some(value) => value
            .as_i64()
            .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?,
    };
    let digest_hex = m
        .get("digest_hex")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "digest required"))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    let raw = hex_decode(digest_hex)
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
    if raw.len() != 32 {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "resource digest must be 32 bytes",
        ));
    }
    let mut digest = [0u8; 32];
    digest.copy_from_slice(&raw);
    Ok(ResourceRef {
        resource_id,
        media_type,
        algorithm,
        digest,
    })
}

fn parse_limit(value: Option<&Json>, label: &str) -> Result<Option<u64>, OlpError> {
    match value {
        None | Some(Json::Null) => Ok(None),
        Some(v) => v
            .as_u64()
            .map(Some)
            .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", format!("{label}: {e}"))),
    }
}

fn parse_option_bool(
    options: &BTreeMap<String, Json>,
    key: &str,
    default: bool,
) -> Result<bool, OlpError> {
    match options.get(key) {
        None => Ok(default),
        Some(value) => value
            .as_bool()
            .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", format!("{key}: {e}"))),
    }
}

fn parse_request(v: &Json) -> Result<Request, OlpError> {
    let m = v
        .as_object()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;

    let domain = match m.get("domain") {
        None => DOMAIN,
        Some(value) => value
            .as_str()
            .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?,
    };
    if domain != DOMAIN {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "invalid resolution request domain",
        ));
    }

    let version = match m.get("version") {
        None => 1,
        Some(value) => value
            .as_i64()
            .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?,
    };
    if version != 1 {
        return Err(OlpError::unsupported(
            "UNSUPPORTED_RESOLUTION_REQUEST_VERSION",
            "unsupported resolution request version",
        ));
    }

    let target_class = m
        .get("target_class")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "target_class required"))?
        .as_str()
        .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?
        .to_string();
    if target_class.is_empty() {
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "target_class must be non-empty text",
        ));
    }
    if !CORE_TARGETS.contains(&target_class.as_str()) {
        if is_absolute_uri(&target_class) {
            return Err(OlpError::unsupported(
                "UNSUPPORTED_TARGET_CLASS",
                "unsupported target class",
            ));
        }
        return Err(malformed(
            "MALFORMED_RESOLUTION_REQUEST",
            "unknown compact target class",
        ));
    }
    if target_class != "evidence" && target_class != "externalResource" {
        return Err(OlpError::unsupported(
            "UNSUPPORTED_TARGET_CLASS",
            "target class is outside executable resolution-v1",
        ));
    }

    let target = m
        .get("target")
        .ok_or_else(|| malformed("MALFORMED_RESOLUTION_REQUEST", "target required"))?
        .clone();
    if target_class == "evidence" {
        parse_evidence_ref(&target)?;
    } else {
        match &target {
            Json::String(uri) => {
                if !is_absolute_uri(uri) {
                    return Err(malformed(
                        "MALFORMED_RESOLUTION_REQUEST",
                        "external resource target must be absolute URI",
                    ));
                }
            }
            Json::Object(wrapper)
                if wrapper.len() == 1 && wrapper.contains_key("resource_ref") =>
            {
                parse_resource_ref(wrapper.get("resource_ref").expect("checked key"))?;
            }
            _ => {
                return Err(malformed(
                    "MALFORMED_RESOLUTION_REQUEST",
                    "external resource target malformed",
                ))
            }
        }
    }

    let accept = match m.get("accept") {
        None => Vec::new(),
        Some(value) => {
            let array = value
                .as_array()
                .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
            let mut values = Vec::with_capacity(array.len());
            let mut seen = BTreeSet::new();
            for item in array {
                let text = item
                    .as_str()
                    .map_err(|e| malformed("MALFORMED_RESOLUTION_REQUEST", e))?;
                if text.is_empty() || !seen.insert(text.to_string()) {
                    return Err(malformed(
                        "MALFORMED_RESOLUTION_REQUEST",
                        "accept members must be unique non-empty text",
                    ));
                }
                values.push(text.to_string());
            }
            values
        }
    };

    if let Some(value) = m.get("as_of") {
        match value {
            Json::Null => {}
            Json::String(text) if time::valid(text) => {}
            _ => {
                return Err(malformed(
                    "MALFORMED_RESOLUTION_REQUEST",
                    "as_of must be RFC 3339 or null",
                ))
            }
        }
    }

    let options = match m.get("options") {
        None => BTreeMap::new(),
        Some(Json::Object(options)) => options.clone(),
        Some(_) => {
            return Err(malformed(
                "MALFORMED_RESOLUTION_REQUEST",
                "options must be an object",
            ))
        }
    };
    for key in options.keys() {
        if !matches!(
            key.as_str(),
            "offline_only"
                | "max_bytes"
                | "max_results"
                | "allow_redirects"
                | "require_fresh"
                | "network_policy_id"
        ) {
            return Err(malformed(
                "MALFORMED_RESOLUTION_REQUEST",
                "unknown resolution option",
            ));
        }
    }

    let offline_only = parse_option_bool(&options, "offline_only", false)?;
    let max_bytes = parse_limit(options.get("max_bytes"), "max_bytes")?;
    let max_results = parse_limit(options.get("max_results"), "max_results")?;
    let allow_redirects = parse_option_bool(&options, "allow_redirects", false)?;
    let require_fresh = parse_option_bool(&options, "require_fresh", false)?;
    if let Some(value) = options.get("network_policy_id") {
        match value {
            Json::Null => {}
            Json::String(uri) if is_absolute_uri(uri) => {}
            _ => {
                return Err(malformed(
                    "MALFORMED_RESOLUTION_REQUEST",
                    "network_policy_id must be absolute URI or null",
                ))
            }
        }
    }

    Ok(Request {
        target_class,
        target,
        accept,
        offline_only,
        max_bytes,
        max_results,
        allow_redirects,
        require_fresh,
    })
}

include!("resolution_part2.rs");
include!("resolution_part3.rs");
include!("resolution_part4.rs");
