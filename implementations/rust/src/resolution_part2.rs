fn arr_str(v: Vec<String>) -> Json { Json::Array(v.into_iter().map(Json::String).collect()) }
fn base(status:&str, errors:Vec<&str>, redirects:Vec<String>, network_requests:i64, freshness:&str)->BTreeMap<String,Json>{
    let mut o=Json::object();
    o.insert("status".into(),Json::String(status.into())); o.insert("matches".into(),Json::Array(vec![])); o.insert("provenance".into(),Json::Array(vec![]));
    o.insert("freshness".into(),Json::String(freshness.into())); o.insert("conflicts".into(),Json::Array(vec![])); o.insert("redirects".into(),arr_str(redirects));
    o.insert("warnings".into(),Json::Array(vec![])); o.insert("errors".into(),Json::Array(errors.into_iter().map(|s|Json::String(s.into())).collect())); o.insert("network_requests".into(),Json::Int(network_requests as i128)); o
}

fn source_freshness(s:&BTreeMap<String,Json>)->Result<String,OlpError>{match s.get("freshness"){None=>Ok("NOT_APPLICABLE".into()),Some(v)=>Ok(v.as_str().map_err(|e|malformed("RESOLVER_RESPONSE_MALFORMED",e))?.to_string())}}
fn size_exceeds(r:&Request,size:u64)->bool{r.max_bytes.is_some_and(|m|size>m)}

fn uri_scheme(uri:&str)->&str{uri.split_once(':').map(|x|x.0).unwrap_or("")}
fn http_host(uri:&str)->Option<String>{
    let rest=uri.strip_prefix("http://").or_else(||uri.strip_prefix("https://"))?;
    let authority=rest.split(['/', '?', '#']).next().unwrap_or("");
    let hostport=authority.rsplit('@').next().unwrap_or("");
    if hostport.starts_with('['){let end=hostport.find(']')?;Some(hostport[1..end].to_string())}else{Some(hostport.split(':').next().unwrap_or("").to_string())}
}
// IpAddr::from_str accepts only dotted-quad IPv4, but the C resolver a deployment
// later hands the host to also accepts decimal, hexadecimal, octal and short forms,
// all denoting the same address. Treating an unparseable host as a public DNS name
// let a loopback, private-range or metadata-service target pass this check with no
// DNS involvement. Character classes are validated explicitly so the parse cannot
// diverge from inet_aton on padding, sign or radix handling.
fn ipv4_part(text:&str)->Option<u64>{
    if text.is_empty(){return None;}
    let lower=text.to_ascii_lowercase();
    if let Some(body)=lower.strip_prefix("0x"){
        if body.is_empty()||!body.bytes().all(|b|b.is_ascii_hexdigit()){return None;}
        return u64::from_str_radix(body,16).ok();
    }
    if lower.len()>1&&lower.starts_with('0'){
        let body=&lower[1..];
        if !body.bytes().all(|b|(b'0'..=b'7').contains(&b)){return None;}
        return u64::from_str_radix(body,8).ok();
    }
    if !lower.bytes().all(|b|b.is_ascii_digit()){return None;}
    lower.parse::<u64>().ok()
}
fn ipv4_literal(host:&str)->Option<Ipv4Addr>{
    let parts:Vec<&str>=host.split('.').collect();
    if parts.is_empty()||parts.len()>4{return None;}
    let mut values=Vec::with_capacity(parts.len());
    for part in &parts{values.push(ipv4_part(part)?);}
    let (leading,tail)=values.split_at(values.len()-1);
    let tail=tail[0];
    if leading.iter().any(|v|*v>0xFF){return None;}
    let shift=8*(4-leading.len() as u32);
    if tail>=(1u64<<shift){return None;}
    let mut packed=tail;
    for (index,value) in leading.iter().enumerate(){packed|=value<<(8*(3-index as u32));}
    Some(Ipv4Addr::from((packed as u32).to_be_bytes()))
}
// A DNS name's final label may not be entirely numeric, so a host whose labels are
// all numeric-looking is an address literal however it is spelled and must never be
// treated as a public name when it fails to parse.
fn is_address_literal_attempt(host:&str)->bool{
    host.split('.').all(|part|!part.is_empty()&&(part.bytes().all(|b|b.is_ascii_digit())||part.to_ascii_lowercase().starts_with("0x")))
}
fn blocked_network_target(uri:&str)->bool{
    if !matches!(uri_scheme(uri),"http"|"https"){return false;}
    let Some(host)=http_host(uri) else{return true;}; if host.is_empty(){return true;} let lower=host.to_ascii_lowercase(); if lower=="localhost"||lower.ends_with(".localhost"){return true;}
    let ip=match host.parse::<IpAddr>(){
        Ok(parsed)=>parsed,
        Err(_)=>match ipv4_literal(&lower){Some(v4)=>IpAddr::V4(v4),None=>return is_address_literal_attempt(&lower)},
    };
    match ip{
        IpAddr::V4(v)=>v.is_private()||v.is_loopback()||v.is_link_local()||v.is_multicast()||v.is_unspecified()||v.octets()[0]==0||v.octets()[0]>=240,
        IpAddr::V6(v)=>v.is_loopback()||v.is_multicast()||v.is_unspecified()||is_ipv6_unique_local(v)||is_ipv6_link_local(v),
    }
}
fn is_ipv6_unique_local(v:Ipv6Addr)->bool{v.segments()[0]&0xfe00==0xfc00}
fn is_ipv6_link_local(v:Ipv6Addr)->bool{v.segments()[0]&0xffc0==0xfe80}

