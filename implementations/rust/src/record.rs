//! Specification 0003 RecordV1 validation and OLP-CI-1 identity.
use std::collections::{BTreeMap,BTreeSet};
use crate::{cbor::{self,Value},error::OlpError,json::Json,sha256,util::{base64url_no_pad,hex_encode,is_absolute_uri,is_semantic_identifier}};

const FIELDS:[&str;7]=["envelope_version","type","content","semantic_bindings","profiles","relationships","extensions"];

fn valid_record_value(v:&Json,depth:usize)->bool{
 if depth>cbor::MAX_DEPTH{return false;}
 match v{
  Json::Null|Json::Bool(_)|Json::String(_)=>true,
  Json::Int(n)=>*n>=-(1i128<<64)&&*n<=(1i128<<64)-1,
  Json::Array(a)=>a.len()<=cbor::MAX_COLLECTION_ITEMS&&a.iter().all(|x|valid_record_value(x,depth+1)),
  Json::Object(m) if m.len()==1&&m.contains_key("$bytes")=>m.get("$bytes").is_some_and(|x|x.as_str().ok().is_some_and(|h|crate::util::hex_decode(h).is_ok())),
  Json::Object(m) if m.len()==1&&m.contains_key("$map")=>m.get("$map").is_some_and(|entries|entries.as_array().ok().is_some_and(|a|a.len()<=cbor::MAX_COLLECTION_ITEMS&&a.iter().all(|entry|entry.as_array().ok().is_some_and(|pair|pair.len()==2&&matches!(&pair[0],Json::String(_))&&valid_record_value(&pair[1],depth+1))))),
  Json::Object(m)=>m.len()<=cbor::MAX_COLLECTION_ITEMS&&m.values().all(|x|valid_record_value(x,depth+1)),
 }
}

fn obj_or_empty<'a>(o:&'a BTreeMap<String,Json>,key:&str)->Result<BTreeMap<String,Json>,OlpError>{match o.get(key){None=>Ok(BTreeMap::new()),Some(Json::Object(m))=>Ok(m.clone()),Some(_)=>Err(OlpError::malformed("NONCONFORMING",format!("{key} must be a map")))}}

pub fn identity_preimage(record:&Json)->Result<Value,OlpError>{
    let o=record.as_object().map_err(|e|OlpError::malformed("NONCONFORMING",e))?;
    for k in o.keys(){if !FIELDS.contains(&k.as_str()){return Err(OlpError::malformed("NONCONFORMING",format!("unknown RecordV1 field {k}")));}}
    let version=o.get("envelope_version").ok_or_else(||OlpError::malformed("NONCONFORMING","missing envelope_version"))?.as_i64().map_err(|e|OlpError::malformed("NONCONFORMING",e))?;
    if version!=1{return Err(OlpError::malformed("NONCONFORMING","RecordV1 envelope_version must equal 1"));}
    let typ=o.get("type").ok_or_else(||OlpError::malformed("NONCONFORMING","missing type"))?.as_str().map_err(|e|OlpError::malformed("NONCONFORMING",e))?;
    if !is_semantic_identifier(typ){return Err(OlpError::malformed("NONCONFORMING","invalid record type SemanticIdentifier"));}
    let content=o.get("content").ok_or_else(||OlpError::malformed("NONCONFORMING","missing content"))?;
    if !valid_record_value(content,0){return Err(OlpError::malformed("NONCONFORMING","invalid record content value"));}
    let semantic=obj_or_empty(o,"semantic_bindings")?;
    for(k,v)in &semantic{if !is_semantic_identifier(k)||!valid_record_value(v,0){return Err(OlpError::malformed("NONCONFORMING","invalid semantic binding"));}}
    let profiles:Vec<String>=match o.get("profiles"){None=>Vec::new(),Some(Json::Array(a))=>{let mut out=Vec::new();let mut seen=BTreeSet::new();for x in a{let s=x.as_str().map_err(|e|OlpError::malformed("NONCONFORMING",e))?;if !is_semantic_identifier(s)||!seen.insert(s.to_string()){return Err(OlpError::malformed("NONCONFORMING","profiles must contain unique SemanticIdentifiers"));}out.push(s.to_string());}out},Some(_)=>return Err(OlpError::malformed("NONCONFORMING","profiles must be an array"))};
    let relationships:Vec<Json>=match o.get("relationships"){None=>Vec::new(),Some(Json::Array(a))=>{if !a.iter().all(|x|valid_record_value(x,0)){return Err(OlpError::malformed("NONCONFORMING","invalid relationship value"));}a.clone()},Some(_)=>return Err(OlpError::malformed("NONCONFORMING","relationships must be an array"))};
    let extensions=obj_or_empty(o,"extensions")?;
    for(k,v)in &extensions{if !is_absolute_uri(k)||!valid_record_value(v,0){return Err(OlpError::malformed("NONCONFORMING","invalid record extension"));}}
    let mut profiles_sorted=profiles;profiles_sorted.sort_by(|a,b|a.as_bytes().cmp(b.as_bytes()));
    Ok(Value::Array(vec![
        Value::Text("OLP-RECORD".into()),Value::Int(1),Value::Text(typ.into()),
        cbor::from_adapter_json(content).map_err(|e|OlpError::malformed("NONCONFORMING",e))?,
        cbor::adapter_string_map(&semantic).map_err(|e|OlpError::malformed("NONCONFORMING",e))?,
        Value::Array(profiles_sorted.into_iter().map(Value::Text).collect()),
        Value::Array(relationships.iter().map(cbor::from_adapter_json).collect::<Result<Vec<_>,_>>().map_err(|e|OlpError::malformed("NONCONFORMING",e))?),
        cbor::adapter_string_map(&extensions).map_err(|e|OlpError::malformed("NONCONFORMING",e))?,
    ]))
}

pub fn identity_bytes(record:&Json)->Result<Vec<u8>,OlpError>{cbor::encode(&identity_preimage(record)?).map_err(|e|OlpError::malformed("NONCONFORMING",e))}
pub fn identity_digest(record:&Json)->Result<[u8;32],OlpError>{Ok(sha256::digest(&identity_bytes(record)?))}
pub fn identity_output(record:&Json)->Result<Json,OlpError>{let bytes=identity_bytes(record)?;let digest=sha256::digest(&bytes);let mut m=Json::object();m.insert("identity_bytes_hex".into(),Json::String(hex_encode(&bytes)));m.insert("identity_bytes_length".into(),Json::Int(bytes.len()as i128));m.insert("record_identity_digest_hex".into(),Json::String(hex_encode(&digest)));m.insert("record_identity_text".into(),Json::String(format!("r1_{}",base64url_no_pad(&digest))));Ok(Json::Object(m))}
