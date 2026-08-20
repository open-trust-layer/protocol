use crate::json::Json;

pub fn hex_decode(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 { return Err("hex string must have even length".into()); }
    let mut out=Vec::with_capacity(s.len()/2); let b=s.as_bytes();
    fn nib(c:u8)->Result<u8,String>{match c{b'0'..=b'9'=>Ok(c-b'0'),b'a'..=b'f'=>Ok(c-b'a'+10),b'A'..=b'F'=>Ok(c-b'A'+10),_=>Err("invalid hexadecimal string".into())}}
    let mut i=0; while i<b.len(){out.push((nib(b[i])?<<4)|nib(b[i+1])?);i+=2;} Ok(out)
}
pub fn hex_encode(v:&[u8])->String{const H:&[u8;16]=b"0123456789abcdef";let mut s=String::with_capacity(v.len()*2);for &x in v{s.push(H[(x>>4)as usize]as char);s.push(H[(x&15)as usize]as char);}s}

pub fn base64url_no_pad(data:&[u8])->String{const T:&[u8;64]=b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";let mut out=String::new();let mut i=0;while i+3<=data.len(){let n=((data[i]as u32)<<16)|((data[i+1]as u32)<<8)|data[i+2]as u32;out.push(T[((n>>18)&63)as usize]as char);out.push(T[((n>>12)&63)as usize]as char);out.push(T[((n>>6)&63)as usize]as char);out.push(T[(n&63)as usize]as char);i+=3;}let r=data.len()-i;if r==1{let n=(data[i]as u32)<<16;out.push(T[((n>>18)&63)as usize]as char);out.push(T[((n>>12)&63)as usize]as char);}else if r==2{let n=((data[i]as u32)<<16)|((data[i+1]as u32)<<8);out.push(T[((n>>18)&63)as usize]as char);out.push(T[((n>>12)&63)as usize]as char);out.push(T[((n>>6)&63)as usize]as char);}out}

pub fn is_absolute_uri(s:&str)->bool{let bytes=s.as_bytes();if bytes.len()<3||!bytes[0].is_ascii_alphabetic(){return false;}let mut i=1;while i<bytes.len()&&bytes[i]!=b':'{if !(bytes[i].is_ascii_alphanumeric()||matches!(bytes[i],b'+'|b'.'|b'-')){return false;}i+=1;}i<bytes.len()-1&&bytes[i]==b':' }
pub fn is_core_identifier(s:&str)->bool{let b=s.as_bytes();if b.is_empty()||!b[0].is_ascii_lowercase(){return false;}let mut prev_sep=false;for &c in &b[1..]{if c.is_ascii_lowercase()||c.is_ascii_digit(){prev_sep=false;}else if matches!(c,b'.'|b'-')&&!prev_sep{prev_sep=true;}else{return false;}}!prev_sep}
pub fn is_semantic_identifier(s:&str)->bool{is_core_identifier(s)||is_absolute_uri(s)}

pub fn json_string(v:&Json)->Result<&str,String>{v.as_str()}
pub fn json_string_opt<'a>(obj:&'a std::collections::BTreeMap<String,Json>,key:&str)->Result<Option<&'a str>,String>{match obj.get(key){None=>Ok(None),Some(Json::String(s))=>Ok(Some(s)),Some(_)=>Err(format!("{key} must be a string"))}}

pub fn json_to_bytes_wrapped(value:&Json)->Result<Json,String>{
    match value {
        Json::Object(m) if m.len()==1 && m.contains_key("$bytes") => {
            let s=m.get("$bytes").unwrap().as_str()?; Ok(Json::String(format!("$BYTES:{}",s)))
        }
        Json::Array(a)=>Ok(Json::Array(a.iter().map(json_to_bytes_wrapped).collect::<Result<Vec<_>,_>>()?)),
        Json::Object(m)=>{let mut o=std::collections::BTreeMap::new();for(k,v)in m{o.insert(k.clone(),json_to_bytes_wrapped(v)?);}Ok(Json::Object(o))},
        _=>Ok(value.clone())
    }
}
