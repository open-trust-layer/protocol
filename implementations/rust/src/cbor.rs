//! Deterministic CBOR profile used by OLP-CIE-1 and ProofInputV1.
use std::collections::BTreeMap;
use crate::json::Json;
use crate::util::hex_decode;

pub const MAX_DEPTH: usize = 64;
pub const MAX_COLLECTION_ITEMS: usize = 100_000;
pub const MAX_TEXT_BYTES: usize = 4 * 1024 * 1024;
pub const MAX_BYTE_STRING_BYTES: usize = 16 * 1024 * 1024;
pub const MAX_OUTPUT_BYTES: usize = 32 * 1024 * 1024;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i128),
    Bytes(Vec<u8>),
    Text(String),
    Array(Vec<Value>),
    Map(Vec<(Value, Value)>),
}

fn checked_extend(out: &mut Vec<u8>, bytes: &[u8]) -> Result<(), String> {
    if out.len().saturating_add(bytes.len()) > MAX_OUTPUT_BYTES {
        return Err("deterministic CBOR output exceeds implementation limit".into());
    }
    out.extend_from_slice(bytes);
    Ok(())
}

fn head(major: u8, arg: u64, out: &mut Vec<u8>) -> Result<(), String> {
    let p = major << 5;
    let encoded: Vec<u8> = if arg < 24 {
        vec![p | arg as u8]
    } else if arg <= 0xff {
        vec![p | 24, arg as u8]
    } else if arg <= 0xffff {
        let mut v = vec![p | 25];
        v.extend_from_slice(&(arg as u16).to_be_bytes());
        v
    } else if arg <= 0xffff_ffff {
        let mut v = vec![p | 26];
        v.extend_from_slice(&(arg as u32).to_be_bytes());
        v
    } else {
        let mut v = vec![p | 27];
        v.extend_from_slice(&arg.to_be_bytes());
        v
    };
    checked_extend(out, &encoded)
}

pub fn encode(value: &Value) -> Result<Vec<u8>, String> {
    encode_at(value, 0)
}

fn encode_at(value: &Value, depth: usize) -> Result<Vec<u8>, String> {
    let mut out = Vec::new();
    enc(value, &mut out, depth)?;
    Ok(out)
}

fn enc(value: &Value, out: &mut Vec<u8>, depth: usize) -> Result<(), String> {
    if depth > MAX_DEPTH {
        return Err("CBOR nesting depth exceeds implementation limit".into());
    }
    match value {
        Value::Null => checked_extend(out, &[0xf6])?,
        Value::Bool(false) => checked_extend(out, &[0xf4])?,
        Value::Bool(true) => checked_extend(out, &[0xf5])?,
        Value::Int(number) => {
            if *number >= 0 {
                head(0, u64::try_from(*number).map_err(|_| "CBOR integer too large")?, out)?;
            } else {
                let magnitude = (-1i128).checked_sub(*number).ok_or("CBOR integer overflow")?;
                head(1, u64::try_from(magnitude).map_err(|_| "CBOR negative integer too small")?, out)?;
            }
        }
        Value::Bytes(bytes) => {
            if bytes.len() > MAX_BYTE_STRING_BYTES {
                return Err("CBOR byte string exceeds implementation limit".into());
            }
            head(2, u64::try_from(bytes.len()).map_err(|_| "CBOR byte string too large")?, out)?;
            checked_extend(out, bytes)?;
        }
        Value::Text(text) => {
            let bytes = text.as_bytes();
            if bytes.len() > MAX_TEXT_BYTES {
                return Err("CBOR text string exceeds implementation limit".into());
            }
            head(3, u64::try_from(bytes.len()).map_err(|_| "CBOR text string too large")?, out)?;
            checked_extend(out, bytes)?;
        }
        Value::Array(items) => {
            if items.len() > MAX_COLLECTION_ITEMS {
                return Err("CBOR array exceeds implementation item limit".into());
            }
            head(4, u64::try_from(items.len()).map_err(|_| "CBOR array too large")?, out)?;
            for item in items {
                enc(item, out, depth + 1)?;
            }
        }
        Value::Map(entries) => {
            if entries.len() > MAX_COLLECTION_ITEMS {
                return Err("CBOR map exceeds implementation item limit".into());
            }
            let mut rows = Vec::with_capacity(entries.len());
            let mut accumulated = 1usize; // map head is at least one byte
            for (key, item) in entries {
                // Preserve enclosing depth. The previous implementation called
                // public encode() here, accidentally resetting depth at every
                // nested map and allowing a stack-exhaustion bypass.
                let key_bytes = encode_at(key, depth + 1)?;
                let value_bytes = encode_at(item, depth + 1)?;
                accumulated = accumulated.saturating_add(key_bytes.len()).saturating_add(value_bytes.len());
                if accumulated > MAX_OUTPUT_BYTES {
                    return Err("deterministic CBOR output exceeds implementation limit".into());
                }
                rows.push((key_bytes, value_bytes));
            }
            rows.sort_by(|a, b| a.0.cmp(&b.0));
            for index in 1..rows.len() {
                if rows[index - 1].0 == rows[index].0 {
                    return Err("duplicate canonical CBOR map key".into());
                }
            }
            head(5, u64::try_from(rows.len()).map_err(|_| "CBOR map too large")?, out)?;
            for (key_bytes, value_bytes) in rows {
                checked_extend(out, &key_bytes)?;
                checked_extend(out, &value_bytes)?;
            }
        }
    }
    Ok(())
}

pub fn from_json(value: &Json) -> Result<Value, String> {
    match value {
        Json::Null => Ok(Value::Null),
        Json::Bool(value) => Ok(Value::Bool(*value)),
        Json::Int(value) => Ok(Value::Int(*value)),
        Json::String(value) => {
            if let Some(hex) = value.strip_prefix("$BYTES:") {
                Ok(Value::Bytes(hex_decode(hex)?))
            } else {
                Ok(Value::Text(value.clone()))
            }
        }
        Json::Array(items) => Ok(Value::Array(items.iter().map(from_json).collect::<Result<Vec<_>, _>>()?)),
        Json::Object(map) => {
            let mut rows = Vec::new();
            for (key, item) in map {
                rows.push((Value::Text(key.clone()), from_json(item)?));
            }
            Ok(Value::Map(rows))
        }
    }
}

pub fn from_adapter_json(value: &Json) -> Result<Value, String> {
    match value {
        Json::Object(map) if map.len() == 1 && map.contains_key("$bytes") => {
            let text = map.get("$bytes").unwrap().as_str()?;
            Ok(Value::Bytes(hex_decode(text)?))
        }
        Json::Object(map) if map.len() == 1 && map.contains_key("$map") => {
            let entries = map.get("$map").unwrap().as_array()?;
            if entries.len() > MAX_COLLECTION_ITEMS {
                return Err("$map exceeds adapter item limit".into());
            }
            let mut rows = Vec::with_capacity(entries.len());
            for entry in entries {
                let pair = entry.as_array()?;
                if pair.len() != 2 {
                    return Err("$map entries must be two-element arrays".into());
                }
                let key = from_adapter_json(&pair[0])?;
                if !matches!(key, Value::Text(_) | Value::Int(_)) {
                    return Err("$map keys must be text strings or integer labels".into());
                }
                rows.push((key, from_adapter_json(&pair[1])?));
            }
            // Duplicate abstract keys are rejected by deterministic encode,
            // where equality is defined by canonical key bytes.
            Ok(Value::Map(rows))
        }
        Json::Null => Ok(Value::Null),
        Json::Bool(value) => Ok(Value::Bool(*value)),
        Json::Int(value) => Ok(Value::Int(*value)),
        Json::String(value) => Ok(Value::Text(value.clone())),
        Json::Array(items) => Ok(Value::Array(items.iter().map(from_adapter_json).collect::<Result<Vec<_>, _>>()?)),
        Json::Object(map) => {
            let mut rows = Vec::new();
            for (key, item) in map {
                rows.push((Value::Text(key.clone()), from_adapter_json(item)?));
            }
            Ok(Value::Map(rows))
        }
    }
}

pub fn adapter_string_map(map: &BTreeMap<String, Json>) -> Result<Value, String> {
    let mut rows = Vec::new();
    for (key, value) in map {
        rows.push((Value::Text(key.clone()), from_adapter_json(value)?));
    }
    Ok(Value::Map(rows))
}

pub fn string_map(map: &BTreeMap<String, Json>) -> Result<Value, String> {
    let mut rows = Vec::new();
    for (key, value) in map {
        rows.push((Value::Text(key.clone()), from_json(value)?));
    }
    Ok(Value::Map(rows))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn nested_map_depth_is_bounded() {
        let mut value = Value::Int(0);
        for _ in 0..=MAX_DEPTH {
            value = Value::Map(vec![(Value::Text("k".into()), value)]);
        }
        assert!(encode(&value).is_err());
    }

    #[test]
    fn adapter_map_preserves_integer_and_text_keys() {
        let parsed = crate::json::parse(r#"{"$map":[[1,"int"],["1","text"]]}"#).unwrap();
        let value = from_adapter_json(&parsed).unwrap();
        let encoded = encode(&value).unwrap();
        assert!(!encoded.is_empty());
    }
}
