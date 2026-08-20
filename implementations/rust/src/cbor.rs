//! Deterministic CBOR profile used by OLP-CIE-1 and ProofInputV1.
use std::collections::BTreeMap;
use crate::json::Json;
use crate::util::hex_decode;

#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Value{Null,Bool(bool),Int(i128),Bytes(Vec<u8>),Text(String),Array(Vec<Value>),Map(Vec<(Value,Value)>)}

fn head(major:u8,arg:u64,out:&mut Vec<u8>){let p=major<<5;if arg<24{out.push(p|arg as u8)}else if arg<=0xff{out.extend_from_slice(&[p|24,arg as u8])}else if arg<=0xffff{out.push(p|25);out.extend_from_slice(&(arg as u16).to_be_bytes())}else if arg<=0xffff_ffff{out.push(p|26);out.extend_from_slice(&(arg as u32).to_be_bytes())}else{out.push(p|27);out.extend_from_slice(&arg.to_be_bytes())}}
pub fn encode(v:&Value)->Result<Vec<u8>,String>{let mut out=Vec::new();enc(v,&mut out,0)?;Ok(out)}
fn enc(v:&Value,out:&mut Vec<u8>,depth:usize)->Result<(),String>{if depth>64{return Err("CBOR nesting depth exceeds limit".into());}match v{Value::Null=>out.push(0xf6),Value::Bool(false)=>out.push(0xf4),Value::Bool(true)=>out.push(0xf5),Value::Int(n)=>{if *n>=0{head(0,u64::try_from(*n).map_err(|_|"CBOR integer too large")?,out)}else{let x=(-1i128).checked_sub(*n).ok_or("CBOR integer overflow")?;head(1,u64::try_from(x).map_err(|_|"CBOR negative integer too small")?,out)}},Value::Bytes(b)=>{head(2,b.len()as u64,out);out.extend_from_slice(b)},Value::Text(s)=>{let b=s.as_bytes();head(3,b.len()as u64,out);out.extend_from_slice(b)},Value::Array(a)=>{head(4,a.len()as u64,out);for x in a{enc(x,out,depth+1)?;}},Value::Map(m)=>{let mut rows=Vec::with_capacity(m.len());for(k,v)in m{let kb=encode(k)?;let vb=encode(v)?;rows.push((kb,vb));}rows.sort_by(|a,b|a.0.cmp(&b.0));for i in 1..rows.len(){if rows[i-1].0==rows[i].0{return Err("duplicate canonical CBOR map key".into());}}head(5,rows.len()as u64,out);for(k,v)in rows{out.extend(k);out.extend(v);}}}Ok(())}

pub fn from_json(v:&Json)->Result<Value,String>{match v{Json::Null=>Ok(Value::Null),Json::Bool(b)=>Ok(Value::Bool(*b)),Json::Int(n)=>Ok(Value::Int(*n)),Json::String(s)=>{if let Some(hex)=s.strip_prefix("$BYTES:"){Ok(Value::Bytes(hex_decode(hex)?))}else{Ok(Value::Text(s.clone()))}},Json::Array(a)=>Ok(Value::Array(a.iter().map(from_json).collect::<Result<Vec<_>,_>>()?)),Json::Object(m)=>{let mut rows=Vec::new();for(k,v)in m{rows.push((Value::Text(k.clone()),from_json(v)?));}Ok(Value::Map(rows))}}}

pub fn from_adapter_json(v:&Json)->Result<Value,String>{match v{
    Json::Object(m) if m.len()==1 && m.contains_key("$bytes") => { let s=m.get("$bytes").unwrap().as_str()?; Ok(Value::Bytes(hex_decode(s)?)) },
    Json::Null=>Ok(Value::Null),Json::Bool(b)=>Ok(Value::Bool(*b)),Json::Int(n)=>Ok(Value::Int(*n)),Json::String(s)=>Ok(Value::Text(s.clone())),
    Json::Array(a)=>Ok(Value::Array(a.iter().map(from_adapter_json).collect::<Result<Vec<_>,_>>()?)),
    Json::Object(m)=>{let mut rows=Vec::new();for(k,v)in m{rows.push((Value::Text(k.clone()),from_adapter_json(v)?));}Ok(Value::Map(rows))}
}}
pub fn adapter_string_map(m:&BTreeMap<String,Json>)->Result<Value,String>{let mut rows=Vec::new();for(k,v)in m{rows.push((Value::Text(k.clone()),from_adapter_json(v)?));}Ok(Value::Map(rows))}

pub fn string_map(m:&BTreeMap<String,Json>)->Result<Value,String>{let mut rows=Vec::new();for(k,v)in m{rows.push((Value::Text(k.clone()),from_json(v)?));}Ok(Value::Map(rows))}
