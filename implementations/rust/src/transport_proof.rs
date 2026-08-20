//! Proof-object transport round-trip helper for Milestone 23.
//!
//! This intentionally drives the independent Rust OJVE implementation through
//! its public operation surface, then reconstructs the ordinary conformance
//! proof representation before recomputing Proof Identity.
use std::collections::BTreeMap;
use crate::{error::OlpError,json::Json,proof_identity,transport,util::{hex_decode,hex_encode}};

fn malformed(msg:impl Into<String>)->OlpError{OlpError::malformed("MALFORMED_TRANSPORT_INPUT",msg)}

fn bytes_projection(hex:&str)->Json{let mut m=Json::object();m.insert("$bytes".into(),Json::String(hex.into()));Json::Object(m)}
fn map_projection(entries:Vec<(String,Json)>)->Json{let mut m=Json::object();m.insert("$map".into(),Json::Array(entries.into_iter().map(|(k,v)|Json::Array(vec![Json::String(k),v])).collect()));Json::Object(m)}

fn proof_projection(proof:&Json)->Result<Json,OlpError>{
 let o=proof.as_object().map_err(malformed)?;let mut entries=Vec::new();
 for key in ["type","version","cryptosuite","proofPurpose","verificationMethod"]{entries.push((key.into(),o.get(key).ok_or_else(||malformed(format!("missing proof {key}")))?.clone()));}
 let rc=o.get("recordCommitment").ok_or_else(||malformed("missing recordCommitment"))?.as_object().map_err(malformed)?;
 let alg=rc.get("algorithm").ok_or_else(||malformed("missing commitment algorithm"))?.clone();
 let digest=rc.get("digest_hex").ok_or_else(||malformed("missing commitment digest"))?.as_str().map_err(malformed)?;
 hex_decode(digest).map_err(malformed)?;
 entries.push(("recordCommitment".into(),Json::Array(vec![alg,bytes_projection(digest)])));
 let signature=o.get("proofValue_hex").ok_or_else(||malformed("missing proofValue_hex"))?.as_str().map_err(malformed)?;hex_decode(signature).map_err(malformed)?;
 entries.push(("proofValue".into(),bytes_projection(signature)));
 for key in ["created","expires","domain"]{if let Some(v)=o.get(key){entries.push((key.into(),v.clone()));}}
 for (source,target) in [("challenge_hex","challenge"),("nonce_hex","nonce")]{if let Some(v)=o.get(source){let h=v.as_str().map_err(malformed)?;hex_decode(h).map_err(malformed)?;entries.push((target.into(),bytes_projection(h)));}}
 entries.push(("critical".into(),o.get("critical").cloned().unwrap_or(Json::Array(Vec::new()))));
 let ext=o.get("extensions").cloned().unwrap_or(Json::Object(BTreeMap::new()));
 // Convert the ordinary outer extension object to the pair-preserving transport
 // projection. Nested values retain their normal adapter projection.
 let ext_obj=ext.as_object().map_err(|_|malformed("proof extensions must be object"))?;
 entries.push(("extensions".into(),map_projection(ext_obj.iter().map(|(k,v)|(k.clone(),v.clone())).collect())));
 Ok(map_projection(entries))
}

fn top_map(value:&Json)->Result<BTreeMap<String,Json>,OlpError>{
 let o=value.as_object().map_err(malformed)?;if o.len()!=1||!o.contains_key("$map"){return Err(malformed("decoded transported proof must be $map projection"));}
 let pairs=o.get("$map").unwrap().as_array().map_err(malformed)?;let mut out=BTreeMap::new();for pair in pairs{let a=pair.as_array().map_err(malformed)?;if a.len()!=2{return Err(malformed("proof map entry must contain two elements"));}let k=a[0].as_str().map_err(|_|malformed("proof field key must be text"))?.to_string();if out.insert(k,a[1].clone()).is_some(){return Err(malformed("duplicate transported proof field"));}}Ok(out)
}
fn bytes_hex(v:&Json)->Result<String,OlpError>{let o=v.as_object().map_err(malformed)?;if o.len()!=1||!o.contains_key("$bytes"){return Err(malformed("expected transported byte string"));}let h=o.get("$bytes").unwrap().as_str().map_err(malformed)?;hex_decode(h).map_err(malformed)?;Ok(h.into())}
fn materialize_extensions(v:&Json)->Result<Json,OlpError>{let m=top_map(v)?;Ok(Json::Object(m))}

fn reconstruct(value:&Json)->Result<Json,OlpError>{
 let m=top_map(value)?;let mut out=Json::object();
 for key in ["type","version","cryptosuite","proofPurpose","verificationMethod"]{out.insert(key.into(),m.get(key).ok_or_else(||malformed(format!("missing transported proof {key}")))?.clone());}
 let rc=m.get("recordCommitment").ok_or_else(||malformed("missing transported recordCommitment"))?.as_array().map_err(malformed)?;if rc.len()!=2{return Err(malformed("transported recordCommitment must contain two elements"));}
 let mut r=Json::object();r.insert("algorithm".into(),rc[0].clone());r.insert("digest_hex".into(),Json::String(bytes_hex(&rc[1])?));out.insert("recordCommitment".into(),Json::Object(r));
 out.insert("proofValue_hex".into(),Json::String(bytes_hex(m.get("proofValue").ok_or_else(||malformed("missing transported proofValue"))?)?));
 for key in ["created","expires","domain"]{if let Some(v)=m.get(key){out.insert(key.into(),v.clone());}}
 for (source,target) in [("challenge","challenge_hex"),("nonce","nonce_hex")]{if let Some(v)=m.get(source){out.insert(target.into(),Json::String(bytes_hex(v)?));}}
 out.insert("critical".into(),m.get("critical").cloned().unwrap_or(Json::Array(Vec::new())));
 out.insert("extensions".into(),materialize_extensions(m.get("extensions").unwrap_or(&map_projection(Vec::new())))?);
 Ok(Json::Object(out))
}

pub fn equivalence(input:&Json)->Result<Json,OlpError>{
 let proof=input.get("proof").map_err(malformed)?;let before=proof_identity::proof_identity_digest_for(proof)?;
 let projection=proof_projection(proof)?;
 let mut encode_input=Json::object();encode_input.insert("value".into(),projection);let encoded=transport::operation("encode_ojve",&Json::Object(encode_input))?;
 let ojve=encoded.get("ojve").map_err(malformed)?.clone();let mut decode_input=Json::object();decode_input.insert("ojve".into(),ojve);let decoded=transport::operation("decode_ojve",&Json::Object(decode_input))?;
 let reconstructed=reconstruct(decoded.get("value").map_err(malformed)?)?;let after=proof_identity::proof_identity_digest_for(&reconstructed)?;
 let old_sig=proof.get("proofValue_hex").map_err(malformed)?.as_str().map_err(malformed)?;let new_sig=reconstructed.get("proofValue_hex").map_err(malformed)?.as_str().map_err(malformed)?;
 let mut out=Json::object();out.insert("proof_identity_before_hex".into(),Json::String(hex_encode(&before)));out.insert("proof_identity_after_json_hex".into(),Json::String(hex_encode(&after)));out.insert("identity_preserved".into(),Json::Bool(before==after));out.insert("proof_value_preserved".into(),Json::Bool(old_sig==new_sig));Ok(Json::Object(out))
}
