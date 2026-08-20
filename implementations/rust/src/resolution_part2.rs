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
fn blocked_network_target(uri:&str)->bool{
    if !matches!(uri_scheme(uri),"http"|"https"){return false;}
    let Some(host)=http_host(uri) else{return true;}; if host.is_empty(){return true;} let lower=host.to_ascii_lowercase(); if lower=="localhost"||lower.ends_with(".localhost"){return true;}
    let Ok(ip)=host.parse::<IpAddr>() else{return false;};
    match ip{
        IpAddr::V4(v)=>v.is_private()||v.is_loopback()||v.is_link_local()||v.is_multicast()||v.is_unspecified()||v.octets()[0]==0||v.octets()[0]>=240,
        IpAddr::V6(v)=>v.is_loopback()||v.is_multicast()||v.is_unspecified()||is_ipv6_unique_local(v)||is_ipv6_link_local(v),
    }
}
fn is_ipv6_unique_local(v:Ipv6Addr)->bool{v.segments()[0]&0xfe00==0xfc00}
fn is_ipv6_link_local(v:Ipv6Addr)->bool{v.segments()[0]&0xffc0==0xfe80}

