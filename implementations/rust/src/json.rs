//! Minimal JSON parser/serializer used by the language-neutral adapter.
//!
//! The protocol core does not depend on JSON.  This module exists only for the
//! Milestone 14 JSON-lines conformance boundary.  It intentionally accepts
//! integer JSON numbers only because the OLP 0003/0004 abstract value models do
//! not admit floating-point values.

use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Json {
    Null,
    Bool(bool),
    Int(i128),
    String(String),
    Array(Vec<Json>),
    Object(BTreeMap<String, Json>),
}

impl Json {
    pub fn object() -> BTreeMap<String, Json> { BTreeMap::new() }
    pub fn as_object(&self) -> Result<&BTreeMap<String, Json>, String> {
        match self { Json::Object(v) => Ok(v), _ => Err("expected JSON object".into()) }
    }
    pub fn as_array(&self) -> Result<&[Json], String> {
        match self { Json::Array(v) => Ok(v), _ => Err("expected JSON array".into()) }
    }
    pub fn as_str(&self) -> Result<&str, String> {
        match self { Json::String(v) => Ok(v), _ => Err("expected JSON string".into()) }
    }
    pub fn as_i64(&self) -> Result<i64, String> {
        match self {
            Json::Int(v) => i64::try_from(*v).map_err(|_| "integer outside i64 range".into()),
            _ => Err("expected JSON integer".into()),
        }
    }
    pub fn as_u64(&self) -> Result<u64, String> {
        match self {
            Json::Int(v) if *v >= 0 => u64::try_from(*v).map_err(|_| "integer outside u64 range".into()),
            _ => Err("expected non-negative JSON integer".into()),
        }
    }
    pub fn as_bool(&self) -> Result<bool, String> {
        match self { Json::Bool(v) => Ok(*v), _ => Err("expected JSON boolean".into()) }
    }
    pub fn get<'a>(&'a self, key: &str) -> Result<&'a Json, String> {
        self.as_object()?.get(key).ok_or_else(|| format!("missing JSON property {key:?}"))
    }
    pub fn get_opt<'a>(&'a self, key: &str) -> Result<Option<&'a Json>, String> {
        Ok(self.as_object()?.get(key))
    }
}

pub fn parse(input: &str) -> Result<Json, String> {
    let mut p = Parser { bytes: input.as_bytes(), pos: 0 };
    let value = p.value()?;
    p.ws();
    if p.pos != p.bytes.len() { return Err(format!("trailing JSON data at byte {}", p.pos)); }
    Ok(value)
}

pub fn stringify(value: &Json) -> String {
    let mut out = String::new();
    write_json(value, &mut out);
    out
}

fn write_json(value: &Json, out: &mut String) {
    match value {
        Json::Null => out.push_str("null"),
        Json::Bool(false) => out.push_str("false"),
        Json::Bool(true) => out.push_str("true"),
        Json::Int(v) => out.push_str(&v.to_string()),
        Json::String(v) => write_string(v, out),
        Json::Array(items) => {
            out.push('[');
            for (i, item) in items.iter().enumerate() {
                if i != 0 { out.push(','); }
                write_json(item, out);
            }
            out.push(']');
        }
        Json::Object(map) => {
            out.push('{');
            for (i, (key, value)) in map.iter().enumerate() {
                if i != 0 { out.push(','); }
                write_string(key, out);
                out.push(':');
                write_json(value, out);
            }
            out.push('}');
        }
    }
}

fn write_string(value: &str, out: &mut String) {
    out.push('"');
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c < '\u{20}' => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
}

struct Parser<'a> { bytes: &'a [u8], pos: usize }
impl<'a> Parser<'a> {
    fn ws(&mut self) {
        while self.pos < self.bytes.len() && matches!(self.bytes[self.pos], b' ' | b'\n' | b'\r' | b'\t') { self.pos += 1; }
    }
    fn peek(&mut self) -> Option<u8> { self.ws(); self.bytes.get(self.pos).copied() }
    fn value(&mut self) -> Result<Json, String> {
        match self.peek().ok_or_else(|| "unexpected end of JSON".to_string())? {
            b'n' => { self.literal(b"null")?; Ok(Json::Null) }
            b't' => { self.literal(b"true")?; Ok(Json::Bool(true)) }
            b'f' => { self.literal(b"false")?; Ok(Json::Bool(false)) }
            b'"' => Ok(Json::String(self.string()?)),
            b'[' => self.array(),
            b'{' => self.object(),
            b'-' | b'0'..=b'9' => self.number(),
            other => Err(format!("unexpected JSON byte 0x{other:02x} at {}", self.pos)),
        }
    }
    fn literal(&mut self, lit: &[u8]) -> Result<(), String> {
        self.ws();
        if self.bytes.get(self.pos..self.pos + lit.len()) == Some(lit) { self.pos += lit.len(); Ok(()) }
        else { Err(format!("invalid JSON literal at byte {}", self.pos)) }
    }
    fn string(&mut self) -> Result<String, String> {
        self.ws();
        if self.bytes.get(self.pos) != Some(&b'"') { return Err("expected string".into()); }
        self.pos += 1;
        let mut out = String::new();
        while self.pos < self.bytes.len() {
            let b = self.bytes[self.pos];
            if b == b'"' { self.pos += 1; return Ok(out); }
            if b == b'\\' {
                self.pos += 1;
                let esc = *self.bytes.get(self.pos).ok_or_else(|| "truncated JSON escape".to_string())?;
                self.pos += 1;
                match esc {
                    b'"' => out.push('"'), b'\\' => out.push('\\'), b'/' => out.push('/'),
                    b'b' => out.push('\u{08}'), b'f' => out.push('\u{0c}'), b'n' => out.push('\n'),
                    b'r' => out.push('\r'), b't' => out.push('\t'),
                    b'u' => {
                        let first = self.hex4()?;
                        let scalar = if (0xD800..=0xDBFF).contains(&first) {
                            if self.bytes.get(self.pos..self.pos + 2) != Some(b"\\u") { return Err("high surrogate not followed by low surrogate".into()); }
                            self.pos += 2;
                            let second = self.hex4()?;
                            if !(0xDC00..=0xDFFF).contains(&second) { return Err("invalid low surrogate".into()); }
                            0x10000 + (((first - 0xD800) as u32) << 10) + (second - 0xDC00) as u32
                        } else if (0xDC00..=0xDFFF).contains(&first) { return Err("unpaired low surrogate".into()); }
                        else { first as u32 };
                        out.push(char::from_u32(scalar).ok_or_else(|| "invalid Unicode scalar".to_string())?);
                    }
                    _ => return Err("invalid JSON escape".into()),
                }
                continue;
            }
            if b < 0x20 { return Err("unescaped JSON control character".into()); }
            let rest = std::str::from_utf8(&self.bytes[self.pos..]).map_err(|_| "invalid UTF-8 in JSON string")?;
            let ch = rest.chars().next().ok_or_else(|| "truncated UTF-8".to_string())?;
            out.push(ch);
            self.pos += ch.len_utf8();
        }
        Err("unterminated JSON string".into())
    }
    fn hex4(&mut self) -> Result<u16, String> {
        if self.pos + 4 > self.bytes.len() { return Err("truncated Unicode escape".into()); }
        let mut n = 0u16;
        for _ in 0..4 {
            let b = self.bytes[self.pos]; self.pos += 1;
            n = (n << 4) | match b { b'0'..=b'9' => (b-b'0') as u16, b'a'..=b'f' => (b-b'a'+10) as u16, b'A'..=b'F' => (b-b'A'+10) as u16, _ => return Err("invalid Unicode escape".into()) };
        }
        Ok(n)
    }
    fn number(&mut self) -> Result<Json, String> {
        self.ws(); let start = self.pos;
        if self.bytes.get(self.pos) == Some(&b'-') { self.pos += 1; }
        if self.bytes.get(self.pos) == Some(&b'0') { self.pos += 1; }
        else {
            let first = self.bytes.get(self.pos).copied().ok_or_else(|| "truncated number".to_string())?;
            if !matches!(first,b'1'..=b'9') { return Err("invalid number".into()); }
            while self.pos < self.bytes.len() && self.bytes[self.pos].is_ascii_digit() { self.pos += 1; }
        }
        if self.pos < self.bytes.len() && matches!(self.bytes[self.pos], b'.'|b'e'|b'E') { return Err("floating-point JSON numbers are outside the OLP adapter profile".into()); }
        let s = std::str::from_utf8(&self.bytes[start..self.pos]).map_err(|_| "invalid number")?;
        let n = s.parse::<i128>().map_err(|_| "JSON integer outside supported range")?;
        Ok(Json::Int(n))
    }
    fn array(&mut self) -> Result<Json, String> {
        self.ws(); self.pos += 1; let mut out = Vec::new(); self.ws();
        if self.bytes.get(self.pos) == Some(&b']') { self.pos += 1; return Ok(Json::Array(out)); }
        loop {
            out.push(self.value()?); self.ws();
            match self.bytes.get(self.pos) { Some(b',') => { self.pos += 1; }, Some(b']') => { self.pos += 1; break; }, _ => return Err("expected ',' or ']'".into()) }
        }
        Ok(Json::Array(out))
    }
    fn object(&mut self) -> Result<Json, String> {
        self.ws(); self.pos += 1; let mut out = BTreeMap::new(); self.ws();
        if self.bytes.get(self.pos) == Some(&b'}') { self.pos += 1; return Ok(Json::Object(out)); }
        loop {
            let key = self.string()?; self.ws();
            if self.bytes.get(self.pos) != Some(&b':') { return Err("expected ':'".into()); }
            self.pos += 1; let value = self.value()?;
            if out.insert(key.clone(), value).is_some() { return Err(format!("duplicate JSON property {key:?}")); }
            self.ws();
            match self.bytes.get(self.pos) { Some(b',') => { self.pos += 1; }, Some(b'}') => { self.pos += 1; break; }, _ => return Err("expected ',' or '}'".into()) }
        }
        Ok(Json::Object(out))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn roundtrip() { let v=parse(r#"{"a":[1,true,null,"é"],"z":-2}"#).unwrap(); assert_eq!(parse(&stringify(&v)).unwrap(),v); }
    #[test] fn duplicate_rejected() { assert!(parse(r#"{"a":1,"a":2}"#).is_err()); }
}
