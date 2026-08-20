//! Parsed RFC 9530 Content-Digest semantics for Milestone 24.
//!
//! RFC 8941 Structured Fields parsing belongs to the HTTP stack. This module
//! consumes the parsed dictionary meaning exposed by the conformance fixture:
//! unique algorithm identifiers and byte-sequence values.

use std::collections::BTreeMap;

use crate::{error::OlpError, json::Json, sha256, util::{hex_decode, hex_encode}};

fn malformed(message: impl Into<String>) -> OlpError {
    OlpError::malformed("MALFORMED_CONTENT_DIGEST", message)
}

pub fn operation(input: &Json) -> Result<Json, OlpError> {
    let obj = input.as_object().map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
    let content_hex = obj
        .get("content_hex")
        .map(|v| v.as_str())
        .transpose()
        .map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?
        .unwrap_or("");
    let content = hex_decode(content_hex).map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
    let required = match obj.get("required") {
        None => false,
        Some(Json::Bool(v)) => *v,
        Some(_) => return Err(OlpError::malformed("MALFORMED_INPUT", "required must be boolean")),
    };

    let Some(raw_members) = obj.get("digest_members") else {
        return Ok(absent(required));
    };
    if matches!(raw_members, Json::Null) {
        return Ok(absent(required));
    }
    let items = raw_members
        .as_array()
        .map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
    let mut members: BTreeMap<String, Vec<u8>> = BTreeMap::new();
    for item in items {
        let member = item.as_object().map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
        if member.len() != 2 || !member.contains_key("algorithm") || !member.contains_key("digest_hex") {
            return Err(OlpError::malformed(
                "MALFORMED_INPUT",
                "each digest member must contain exactly algorithm and digest_hex",
            ));
        }
        let algorithm = member
            .get("algorithm")
            .unwrap()
            .as_str()
            .map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
        if algorithm.is_empty() {
            return Err(malformed("Content-Digest algorithm must be non-empty text"));
        }
        if members.contains_key(algorithm) {
            return Err(malformed("duplicate Content-Digest algorithm"));
        }
        let digest = hex_decode(
            member
                .get("digest_hex")
                .unwrap()
                .as_str()
                .map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?,
        )
        .map_err(|e| OlpError::malformed("MALFORMED_INPUT", e))?;
        if algorithm == "sha-256" && digest.len() != 32 {
            return Err(malformed("sha-256 Content-Digest must contain exactly 32 octets"));
        }
        members.insert(algorithm.to_string(), digest);
    }

    let Some(observed) = members.get("sha-256") else {
        let mut out = Json::object();
        out.insert(
            "status".into(),
            Json::String(if required { "UNSUPPORTED" } else { "UNVALIDATED" }.into()),
        );
        out.insert("algorithm".into(), Json::Null);
        return Ok(Json::Object(out));
    };

    let expected = sha256::digest(&content);
    let mut out = Json::object();
    out.insert(
        "status".into(),
        Json::String(if observed.as_slice() == expected { "VALID" } else { "MISMATCH" }.into()),
    );
    out.insert("algorithm".into(), Json::String("sha-256".into()));
    out.insert("expected_digest_hex".into(), Json::String(hex_encode(&expected)));
    out.insert("observed_digest_hex".into(), Json::String(hex_encode(observed)));
    Ok(Json::Object(out))
}

fn absent(required: bool) -> Json {
    let mut out = Json::object();
    out.insert(
        "status".into(),
        Json::String(if required { "MISSING" } else { "NOT_PRESENT" }.into()),
    );
    out.insert("algorithm".into(), Json::Null);
    Json::Object(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn duplicate_algorithm_is_rejected_after_parsing() {
        let mut member_a = Json::object();
        member_a.insert("algorithm".into(), Json::String("sha-256".into()));
        member_a.insert("digest_hex".into(), Json::String("00".repeat(32)));
        let mut member_b = Json::object();
        member_b.insert("algorithm".into(), Json::String("sha-256".into()));
        member_b.insert("digest_hex".into(), Json::String("11".repeat(32)));
        let mut input = Json::object();
        input.insert("digest_members".into(), Json::Array(vec![Json::Object(member_a), Json::Object(member_b)]));
        input.insert("content_hex".into(), Json::String(String::new()));
        assert_eq!(operation(&Json::Object(input)).unwrap_err().reason, "MALFORMED_CONTENT_DIGEST");
    }
}
