//! Independent Specification 0005 EvidenceRefV1 and relationship processing.
use std::collections::{BTreeMap,BTreeSet};
use crate::{cbor::{self,Value},error::OlpError,json::Json,record,util::{hex_decode,hex_encode,is_absolute_uri}};

const DOMAIN:&str="OLP-EVIDENCE-RELATIONSHIP";
const CORE:[&str;7]=["references","derivesFrom","supersedes","corrects","disputes","anchors","countersigns"];

#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]
struct EvidenceRef{kind:i64,digest:[u8;32]}
impl EvidenceRef{
 fn parse(v:&Json)->Result<Self,OlpError>{
  let a=v.as_array().map_err(|_|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","EvidenceRefV1 must be a two-element array"))?;
  if a.len()!=2{return Err(OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","EvidenceRefV1 must be a two-element array"));}
  let kind=a[0].as_i64().map_err(|_|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","EvidenceRef kind must be integer"))?;
  if kind!=0&&kind!=1{return Err(OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","unsupported EvidenceRefV1 kind"));}
  let digest=parse_bytes(&a[1]).map_err(|_|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","identity digest must be bytes"))?;
  let digest:[u8;32]=digest.try_into().map_err(|_|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","identity digest must contain exactly 32 octets"))?;
  Ok(Self{kind,digest})
 }
 fn value(&self)->Value{Value::Array(vec![Value::Int(self.kind as i128),Value::Bytes(self.digest.to_vec())])}
 fn canonical(&self)->Result<Vec<u8>,OlpError>{cbor::encode(&self.value()).map_err(|e|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED",e))}
 fn json(&self)->Json{let mut m=Json::object();m.insert("kind".into(),Json::Int(self.kind as i128));m.insert("identity_digest_hex".into(),Json::String(hex_encode(&self.digest)));Json::Object(m)}
}
fn parse_bytes(v:&Json)->Result<Vec<u8>,String>{match v{Json::Object(m) if m.len()==1&&m.contains_key("$bytes")=>hex_decode(m.get("$bytes").unwrap().as_str()?),_=>Err("expected $bytes wrapper".into())}}
fn ref_from_input(kind:i64,digest:&[u8])->Result<EvidenceRef,OlpError>{if kind!=0&&kind!=1{return Err(OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","unsupported EvidenceRefV1 kind"));}let d:[u8;32]=digest.try_into().map_err(|_|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED","identity digest must contain exactly 32 octets"))?;Ok(EvidenceRef{kind,digest:d})}

pub fn encode_ref_operation(input:&Json)->Result<Json,OlpError>{
 let kind=input.get("kind").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?.as_i64().map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?;
 let hex=input.get("identity_digest_hex").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?.as_str().map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?;
 let digest=hex_decode(hex).map_err(|e|OlpError::malformed("EVIDENCE_REFERENCE_MALFORMED",e))?;
 let r=ref_from_input(kind,&digest)?;let enc=r.canonical()?;let mut o=Json::object();o.insert("evidence_ref_hex".into(),Json::String(hex_encode(&enc)));o.insert("evidence_ref_length".into(),Json::Int(enc.len() as i128));Ok(Json::Object(o))
}

fn critical_set(input:&Json)->Result<BTreeSet<String>,OlpError>{match input.get_opt("understood_critical_qualifiers").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?{None=>Ok(BTreeSet::new()),Some(Json::Array(a))=>a.iter().map(|v|v.as_str().map(str::to_string).map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))).collect(),Some(_)=>Err(OlpError::malformed("MALFORMED_INPUT","understood_critical_qualifiers must be array"))}}
fn allow_unknown(input:&Json)->Result<bool,OlpError>{match input.get_opt("allow_unknown_relation").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?{None=>Ok(false),Some(v)=>v.as_bool().map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))}}

pub fn process_relationship_operation(input:&Json)->Result<Json,OlpError>{
 let record_json=input.get("record").map_err(|e|OlpError::malformed("MALFORMED_INPUT",e))?;
 let record_id=record::identity_digest(record_json)?;
 let ro=record_json.as_object().map_err(|e|OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT",e))?;
 let content=ro.get("content").ok_or_else(||OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","missing relationship content"))?;
 let a=content.as_array().map_err(|_|OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","relationship content must be array"))?;
 if a.len()!=7{return Err(OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","RelationshipStatementV1 must contain seven elements"));}
 if a[0].as_str().map_err(|_|OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","invalid discriminator"))?!=DOMAIN{return Err(OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","invalid relationship discriminator"));}
 let version=a[1].as_i64().map_err(|_|OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","relationship version must be integer"))?;
 if version!=1{return Err(OlpError::unsupported("UNSUPPORTED_RELATIONSHIP_VERSION","unsupported relationship version"));}
 let relation=a[2].as_str().map_err(|_|OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","relation type must be text"))?;
 if relation.is_empty(){return Err(OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","relation type must be non-empty"));}
 let core=CORE.contains(&relation);if !core&&!is_absolute_uri(relation){return Err(OlpError::malformed("MALFORMED_RELATIONSHIP_STATEMENT","extension relation type must be absolute URI"));}
 if !core&&!allow_unknown(input)?{return Err(OlpError::unsupported("UNSUPPORTED_RELATION_TYPE","unsupported relation type"));}
 let subject=match &a[3]{Json::Null=>None,v=>Some(EvidenceRef::parse(v).map_err(|e|OlpError::malformed("INVALID_RELATION_SUBJECT",e.message))?)};
 let oa=a[4].as_array().map_err(|_|OlpError::malformed("INVALID_RELATION_OBJECT","objects must be array"))?;if oa.is_empty(){return Err(OlpError::malformed("INVALID_RELATION_OBJECT","objects must be non-empty"));}
 let mut objects=Vec::new();let mut canonical=Vec::new();let mut seen=BTreeSet::new();for raw in oa{let r=EvidenceRef::parse(raw).map_err(|e|OlpError::malformed("INVALID_RELATION_OBJECT",e.message))?;let cb=r.canonical()?;if !seen.insert(cb.clone()){return Err(OlpError::malformed("DUPLICATE_RELATION_OBJECT","duplicate relationship object"));}canonical.push(cb);objects.push(r);}let mut sorted=canonical.clone();sorted.sort();if canonical!=sorted{return Err(OlpError::malformed("NON_CANONICAL_RELATION_OBJECT_ORDER","objects are not canonically sorted"));}
 let qualifiers:BTreeMap<String,Json>=a[5].as_object().map_err(|_|OlpError::malformed("INVALID_RELATION_QUALIFIER","qualifiers must be map"))?.clone();for k in qualifiers.keys(){if !is_absolute_uri(k){return Err(OlpError::malformed("INVALID_RELATION_QUALIFIER","qualifier key must be absolute URI"));}}
 let ca=a[6].as_array().map_err(|_|OlpError::malformed("INVALID_CRITICAL_RELATIONSHIP_QUALIFIER","critical must be array"))?;let mut critical=Vec::new();let mut cseen=BTreeSet::new();for raw in ca{let s=raw.as_str().map_err(|_|OlpError::malformed("INVALID_CRITICAL_RELATIONSHIP_QUALIFIER","critical member must be text"))?.to_string();if !is_absolute_uri(&s)||!qualifiers.contains_key(&s)||!cseen.insert(s.clone()){return Err(OlpError::malformed("INVALID_CRITICAL_RELATIONSHIP_QUALIFIER","invalid critical qualifier"));}critical.push(s);}let mut csorted=critical.clone();csorted.sort_by(|x,y|x.as_bytes().cmp(y.as_bytes()));if critical!=csorted{return Err(OlpError::malformed("INVALID_CRITICAL_RELATIONSHIP_QUALIFIER","critical qualifiers are not canonically sorted"));}
 let understood=critical_set(input)?;if critical.iter().any(|x|!understood.contains(x)){return Err(OlpError::unsupported("UNSUPPORTED_CRITICAL_RELATIONSHIP_QUALIFIER","unsupported critical relationship qualifier"));}
 if relation=="countersigns"{if subject.is_some(){return Err(OlpError::malformed("INVALID_RELATION_SUBJECT","countersigns subject must be null"));}if objects.iter().any(|x|x.kind!=1){return Err(OlpError::malformed("COUNTERSIGNATURE_TARGET_TYPE_MISMATCH","countersigns targets must be ProofRef"));}}
 else{let s=subject.as_ref().ok_or_else(||OlpError::malformed("INVALID_RELATION_SUBJECT","core relation requires explicit subject"))?;if matches!(relation,"supersedes"|"corrects"|"disputes"){if s.kind!=0||objects.iter().any(|x|x.kind!=0){return Err(OlpError::malformed("INVALID_RELATION_OBJECT","relation requires RecordRef subject and targets"));}if objects.iter().any(|x|x==s){return Err(OlpError::malformed("RELATION_SUBJECT_OBJECT_CONFLICT","subject cannot target itself"));}}if relation=="anchors"&&s.kind!=0{return Err(OlpError::malformed("INVALID_RELATION_SUBJECT","anchors subject must be RecordRef"));}}
 if subject.as_ref().is_some_and(|x|x.kind==0&&x.digest==record_id)||objects.iter().any(|x|x.kind==0&&x.digest==record_id){return Err(OlpError::malformed("RELATION_SUBJECT_OBJECT_CONFLICT","relationship record cannot self-reference"));}
 let mut out=Json::object();out.insert("relationship_record_identity_hex".into(),Json::String(hex_encode(&record_id)));out.insert("relation_type".into(),Json::String(relation.into()));out.insert("subject".into(),subject.as_ref().map(|x|x.json()).unwrap_or(Json::Null));out.insert("objects".into(),Json::Array(objects.iter().map(|x|x.json()).collect()));out.insert("critical".into(),Json::Array(critical.iter().cloned().map(Json::String).collect()));
 let edges=objects.iter().map(|target|{let mut e=Json::object();e.insert("subject".into(),subject.as_ref().map(|x|x.json()).unwrap_or(Json::Null));e.insert("relation_type".into(),Json::String(relation.into()));e.insert("object".into(),target.json());e.insert("relationship_record_identity_hex".into(),Json::String(hex_encode(&record_id)));Json::Object(e)}).collect();out.insert("projected_edges".into(),Json::Array(edges));Ok(Json::Object(out))
}
