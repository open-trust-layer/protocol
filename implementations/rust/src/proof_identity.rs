//! Specification 0005 deterministic Proof Identity (OLP-PIE-1).

use crate::{cbor::{self,Value},error::OlpError,json::Json,proof,sha256,util::hex_encode};

pub fn proof_identity_bytes_for(proof_value:&Json)->Result<Vec<u8>,OlpError>{
 let parsed=proof::parse_proof(proof_value)?;
 proof::validate_structure(&parsed)?;
 let proof_input=proof::proof_input_bytes(&parsed)?;
 cbor::encode(&Value::Array(vec![
  Value::Text("OLP-PROOF-ID".into()),
  Value::Int(1),
  Value::Bytes(proof_input),
  Value::Bytes(parsed.signature),
 ])).map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))
}

pub fn proof_identity_digest_for(proof_value:&Json)->Result<[u8;32],OlpError>{
 Ok(sha256::digest(&proof_identity_bytes_for(proof_value)?))
}

pub fn proof_identity_operation(input:&Json)->Result<Json,OlpError>{
 let proof_value=input.get("proof").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?;
 let encoded=proof_identity_bytes_for(proof_value)?;
 let digest=sha256::digest(&encoded);
 let mut out=Json::object();
 out.insert("proof_identity_bytes_hex".into(),Json::String(hex_encode(&encoded)));
 out.insert("proof_identity_bytes_length".into(),Json::Int(encoded.len() as i128));
 out.insert("proof_identity_digest_hex".into(),Json::String(hex_encode(&digest)));
 Ok(Json::Object(out))
}
