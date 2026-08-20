//! Deterministic CBOR completion for the Milestone 23 transport adapter.
//!
//! The independently implemented OJVE/parser core lives in `transport.rs`.
//! This helper adds the exact single-envelope CBOR projection required by the
//! M23 interoperability contract without changing the frozen core CBOR rules.

use crate::{
    cbor::{self, Value},
    error::OlpError,
    json::Json,
    transport,
    util::hex_encode,
};

fn malformed(message: impl Into<String>) -> OlpError {
    OlpError::malformed("MALFORMED_TRANSPORT_INPUT", message)
}

fn unsupported_cbor(message: impl Into<String>) -> OlpError {
    OlpError::unsupported("UNSUPPORTED_TRANSPORT_CBOR_VALUE", message)
}

fn envelope_cbor(message_type: &str, payload_projection: &Json) -> Result<Vec<u8>, OlpError> {
    let payload = cbor::from_adapter_json(payload_projection).map_err(unsupported_cbor)?;
    cbor::encode(&Value::Array(vec![
        Value::Text("OLP-TRANSPORT".into()),
        Value::Int(1),
        Value::Text(message_type.into()),
        payload,
    ]))
    .map_err(unsupported_cbor)
}

pub fn encode_envelope(input: &Json) -> Result<Json, OlpError> {
    // Run the independent transport implementation first so malformed message
    // types, OJVE values, and resource limits keep their native classification.
    let base = transport::operation("encode_transport_envelope", input)?;
    let message_type = input
        .get("message_type")
        .map_err(malformed)?
        .as_str()
        .map_err(malformed)?;
    let payload = input.get("payload").map_err(malformed)?;
    let encoded_cbor = envelope_cbor(message_type, payload)?;

    let mut out = base.as_object().map_err(malformed)?.clone();
    out.insert("cbor_hex".into(), Json::String(hex_encode(&encoded_cbor)));
    out.insert(
        "abstract".into(),
        Json::Array(vec![
            Json::String("OLP-TRANSPORT".into()),
            Json::Int(1),
            Json::String(message_type.into()),
            payload.clone(),
        ]),
    );
    Ok(Json::Object(out))
}

pub fn record_equivalence(input: &Json) -> Result<Json, OlpError> {
    let base = transport::operation("transport_record_equivalence", input)?;
    let record = input.get("record").map_err(malformed)?.clone();

    let mut envelope_input = Json::object();
    envelope_input.insert("message_type".into(), Json::String("record".into()));
    envelope_input.insert("payload".into(), record);
    let envelope = encode_envelope(&Json::Object(envelope_input))?;

    let mut out = base.as_object().map_err(malformed)?.clone();
    out.insert("json".into(), envelope.get("json").map_err(malformed)?.clone());
    out.insert(
        "cbor_hex".into(),
        envelope.get("cbor_hex").map_err(malformed)?.clone(),
    );
    Ok(Json::Object(out))
}
