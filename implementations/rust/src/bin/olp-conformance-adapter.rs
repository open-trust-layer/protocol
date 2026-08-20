use std::io::{self, Read};
use olp_rust::{json::{self, Json, MAX_JSON_BYTES}, CAPABILITIES};

fn response_ok(output: Json) -> Json {
    let mut m = Json::object();
    m.insert("protocol".into(), Json::String("olp-conformance-adapter-v1".into()));
    m.insert("ok".into(), Json::Bool(true));
    m.insert("output".into(), output);
    Json::Object(m)
}

fn response_err(classification: &str, reason: &str, message: &str) -> Json {
    let mut e = Json::object();
    e.insert("classification".into(), Json::String(classification.into()));
    e.insert("reason".into(), Json::String(reason.into()));
    e.insert("message".into(), Json::String(message.into()));
    let mut m = Json::object();
    m.insert("protocol".into(), Json::String("olp-conformance-adapter-v1".into()));
    m.insert("ok".into(), Json::Bool(false));
    m.insert("error".into(), Json::Object(e));
    Json::Object(m)
}

fn handle_request(request: Json) -> Json {
    let object = match request.as_object() {
        Ok(value) => value,
        Err(error) => return response_err("MALFORMED", "MALFORMED_REQUEST", &error),
    };
    let protocol = match object.get("protocol").and_then(|value| value.as_str().ok()) {
        Some(value) => value,
        None => return response_err("MALFORMED", "MALFORMED_REQUEST", "protocol must be a string"),
    };
    if protocol != "olp-conformance-adapter-v1" {
        return response_err("MALFORMED", "PROTOCOL_MISMATCH", "protocol mismatch");
    }
    let operation = match object.get("operation").and_then(|value| value.as_str().ok()) {
        Some(value) => value,
        None => return response_err("MALFORMED", "MALFORMED_REQUEST", "operation must be a string"),
    };
    if operation == "capabilities" {
        let mut output = Json::object();
        output.insert(
            "capabilities".into(),
            Json::Array(CAPABILITIES.iter().map(|item| Json::String((*item).into())).collect()),
        );
        return response_ok(Json::Object(output));
    }
    let input = match object.get("input") {
        None => Json::Object(Json::object()),
        Some(Json::Object(map)) => Json::Object(map.clone()),
        Some(_) => return response_err("MALFORMED", "MALFORMED_REQUEST", "input must be an object"),
    };
    match olp_rust::execute(operation, &input) {
        Ok(value) => response_ok(value),
        Err(error) => response_err(error.classification, &error.reason, &error.message),
    }
}

fn main() {
    let mut raw = Vec::new();
    if io::stdin().take((MAX_JSON_BYTES + 2) as u64).read_to_end(&mut raw).is_err() {
        println!("{}", json::stringify(&response_err("MALFORMED", "MALFORMED_INPUT", "failed to read request")));
        return;
    }
    if raw.len() > MAX_JSON_BYTES + 1 {
        println!("{}", json::stringify(&response_err("MALFORMED", "REQUEST_TOO_LARGE", "request exceeds adapter size limit")));
        return;
    }
    let raw = match std::str::from_utf8(&raw) {
        Ok(value) => value,
        Err(_) => {
            println!("{}", json::stringify(&response_err("MALFORMED", "INVALID_JSON", "request is not valid UTF-8")));
            return;
        }
    };
    let lines: Vec<&str> = raw.lines().filter(|line| !line.trim().is_empty()).collect();
    let response = if lines.len() != 1 {
        response_err("MALFORMED", "REQUEST_COUNT", "expected exactly one request")
    } else {
        match json::parse(lines[0]) {
            Err(error) => response_err("MALFORMED", "INVALID_JSON", &error),
            Ok(request) => handle_request(request),
        }
    };
    println!("{}", json::stringify(&response));
}
