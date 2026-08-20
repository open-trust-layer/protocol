// Specification 0009 deterministic, offline-first resolution core.
//
// This module consumes caller-supplied resolver snapshots. It performs no network I/O.

use std::collections::{BTreeMap, BTreeSet};
use std::net::{IpAddr, Ipv6Addr};

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
    as_of: Option<String>,
    options: BTreeMap<i64, Json>,
}

fn obj(v:&Json)->Result<&BTreeMap<String,Json>,OlpError>{match v{Json::Object(m)=>Ok(m),_=>Err(OlpError::Malformed("object required".into()))}}
fn arr(v:&Json)->Result<&Vec<Json>,OlpError>{match v{Json::Array(a)=>Ok(a),_=>Err(OlpError::Malformed("array required".into()))}}
fn text(v:&Json)->Result<&str,OlpError>{match v{Json::String(s)=>Ok(s),_=>Err(OlpError::Malformed("text required".into()))}}
fn int(v:&Json)->Result<i64,OlpError>{match v{Json::Int(n)=>Ok(*n),_=>Err(OlpError::Malformed("integer required".into()))}}
fn boolv(v:&Json)->Result<bool,OlpError>{match v{Json::Bool(b)=>Ok(*b),_=>Err(OlpError::Malformed("boolean required".into()))}}

fn evidence_ref_from_json(v:&Json)->Result<EvidenceRef,OlpError>{
    let m=obj(v)?; let kind=int(m.get("kind").ok_or_else(||OlpError::Malformed("kind required".into()))?)?;
    if kind!=0 && kind!=1{return Err(OlpError::Malformed("invalid evidence kind".into()))}
    let raw=hex_decode(text(m.get("identity_digest_hex").ok_or_else(||OlpError::Malformed("digest required".into()))?)?)?;
    if raw.len()!=32{return Err(OlpError::Malformed("evidence digest must be 32 bytes".into()))}
    let mut digest=[0u8;32]; digest.copy_from_slice(&raw); Ok(EvidenceRef{kind,digest})
}
fn evidence_ref_from_value(v:&Json)->Result<EvidenceRef,OlpError>{
    let a=arr(v)?; if a.len()!=2{return Err(OlpError::Malformed("EvidenceRefV1 must have 2 elements".into()))}
    let kind=int(&a[0])?; let raw=match &a[1]{Json::Bytes(b)=>b,_=>return Err(OlpError::Malformed("EvidenceRefV1 digest must be bytes".into()))};
    if raw.len()!=32{return Err(OlpError::Malformed("EvidenceRefV1 digest length".into()))}; let mut digest=[0u8;32]; digest.copy_from_slice(raw); Ok(EvidenceRef{kind,digest})
}
fn evidence_json(r:&EvidenceRef)->Json{Json::Object(BTreeMap::from([("identity_digest_hex".into(),Json::String(hex_encode(&r.digest))),("kind".into(),Json::Int(r.kind))]))}
fn resource_ref_from_json(v:&Json)->Result<ResourceRef,OlpError>{
    let m=obj(v)?; let id=m.get("resource_id").and_then(|v|match v{Json::String(s)=>Some(s.clone()),Json::Null=>None,_=>None});
    let media=text(m.get("media_type").ok_or_else(||OlpError::Malformed("media_type required".into()))?)?.to_string();
    let alg=int(m.get("hash_algorithm").ok_or_else(||OlpError::Malformed("hash_algorithm required".into()))?)?;
    let raw=hex_decode(text(m.get("digest_hex").ok_or_else(||OlpError::Malformed("digest required".into()))?)?)?; if raw.len()!=32{return Err(OlpError::Malformed("resource digest must be 32 bytes".into()))}; let mut digest=[0u8;32];digest.copy_from_slice(&raw); Ok(ResourceRef{resource_id:id,media_type:media,algorithm:alg,digest})
}
fn resource_ref_from_value(v:&Json)->Result<ResourceRef,OlpError>{
    let a=arr(v)?; if a.len()!=4{return Err(OlpError::Malformed("ResourceRefV1 must have 4 elements".into()))}
    let id=match &a[0]{Json::Null=>None,Json::String(s)=>Some(s.clone()),_=>return Err(OlpError::Malformed("resource id".into()))}; let media=text(&a[1])?.to_string(); let alg=int(&a[2])?; let raw=match &a[3]{Json::Bytes(b)=>b,_=>return Err(OlpError::Malformed("resource digest bytes".into()))}; if raw.len()!=32{return Err(OlpError::Malformed("resource digest length".into()))}; let mut digest=[0u8;32];digest.copy_from_slice(raw);Ok(ResourceRef{resource_id:id,media_type:media,algorithm:alg,digest})
}
fn parse_request(v:&Json)->Result<Request,OlpError>{
    let m=obj(v)?;
    if m.get("domain").map(text).transpose()?.unwrap_or(DOMAIN)!=DOMAIN{return Err(OlpError::Malformed("invalid resolution request domain".into()))}
    if m.get("version").map(int).transpose()?.unwrap_or(1)!=1{return Err(OlpError::Unsupported("UNSUPPORTED_RESOLUTION_REQUEST_VERSION".into()))}
    let tc=text(m.get("target_class").ok_or_else(||OlpError::Malformed("target_class required".into()))?)?.to_string();
    if !CORE_TARGETS.contains(&tc.as_str()){return Err(OlpError::Unsupported("UNSUPPORTED_TARGET_CLASS".into()))}
    if tc!="evidence" && tc!="externalResource"{return Err(OlpError::Unsupported("UNSUPPORTED_TARGET_CLASS".into()))}
    let target=m.get("target").ok_or_else(||OlpError::Malformed("target required".into()))?.clone();
    let accept=match m.get("accept"){None=>vec![],Some(Json::Array(a))=>a.iter().map(|v|text(v).map(str::to_string)).collect::<Result<Vec<_>,_>>()?,_=>return Err(OlpError::Malformed("accept must be array".into()))};
    let as_of=m.get("as_of").map(text).transpose()?.map(str::to_string);
    let mut options=BTreeMap::new(); if let Some(Json::Object(o))=m.get("options") { for (k,v) in o { let label=match k.as_str(){"offline_only"=>0,"max_bytes"=>1,"max_results"=>2,"allow_redirects"=>3,"require_fresh"=>4,"network_policy_id"=>5,_=>continue}; options.insert(label,v.clone()); }}
    if tc=="externalResource" { if let Json::String(s)=&target { if !is_absolute_uri(s){return Err(OlpError::Malformed("externalResource target must be absolute URI".into()))} } }
    Ok(Request{target_class:tc,target,accept,as_of,options})
}
fn opt_bool(r:&Request,k:i64,default:bool)->Result<bool,OlpError>{match r.options.get(&k){None=>Ok(default),Some(v)=>boolv(v)}}
fn opt_int(r:&Request,k:i64)->Result<Option<i64>,OlpError>{match r.options.get(&k){None=>Ok(None),Some(v)=>Ok(Some(int(v)?))}}
fn fresh(source:&BTreeMap<String,Json>)->String{source.get("freshness").and_then(|v|match v{Json::String(s)=>Some(s.clone()),_=>None}).unwrap_or_else(||"UNKNOWN".into())}

include!("resolution_part2.rs");
include!("resolution_part3.rs");
include!("resolution_part4.rs");
