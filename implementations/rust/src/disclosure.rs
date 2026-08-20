//! Independent Rust disclosure planner for OLP Specification 0010.
//!
//! The planner selects exact immutable objects and explicit task dependencies.
//! It never performs ambient network I/O, field-level redaction, global graph
//! closure, or a protocol-global privacy/completeness judgment.

use std::collections::{BTreeMap, BTreeSet, VecDeque};

use crate::{
    cbor::{self, Value},
    error::OlpError,
    json::Json,
    proof_identity, record, sha256,
    util::{hex_decode, hex_encode, is_absolute_uri, is_semantic_identifier},
};

const DOMAIN: &str = "OLP-DISCLOSURE-REQUEST";
const VERSION: i64 = 1;
const PRIVACY_WARNINGS: [&str; 11] = [
    "STABLE_PRINCIPAL_CORRELATION",
    "STABLE_VERIFICATION_METHOD_CORRELATION",
    "SAME_SUBJECT_LINK_DISCLOSED",
    "UNRELATED_ROLE_DISCLOSURE",
    "UNRELATED_AUTHORITY_DISCLOSURE",
    "EXCESS_LIFECYCLE_HISTORY",
    "NETWORK_RESOLUTION_LEAKAGE",
    "BUNDLE_MANIFEST_CORRELATION",
    "SELF_CONTAINED_OVERDISCLOSURE",
    "EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN",
    "GLOBAL_COMPLETENESS_NOT_ESTABLISHED",
];

fn malformed(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::malformed(reason, message)
}
fn unsupported(reason: &str, message: impl Into<String>) -> OlpError {
    OlpError::unsupported(reason, message)
}

fn parse_bytes(v: &Json, reason: &str) -> Result<Vec<u8>, OlpError> {
    match v {
        Json::Object(m) if m.len() == 1 && m.contains_key("$bytes") => {
            let text = m["$bytes"]
                .as_str()
                .map_err(|e| malformed(reason, e))?;
            hex_decode(text).map_err(|e| malformed(reason, e))
        }
        _ => Err(malformed(reason, "expected $bytes wrapper")),
    }
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct EvidenceRef {
    kind: i64,
    digest: [u8; 32],
}
impl EvidenceRef {
    fn parse(v: &Json) -> Result<Self, OlpError> {
        let a = v
            .as_array()
            .map_err(|_| malformed("EVIDENCE_REFERENCE_MALFORMED", "EvidenceRefV1 must be array"))?;
        if a.len() != 2 {
            return Err(malformed("EVIDENCE_REFERENCE_MALFORMED", "EvidenceRefV1 must contain two elements"));
        }
        let kind = a[0]
            .as_i64()
            .map_err(|_| malformed("EVIDENCE_REFERENCE_MALFORMED", "EvidenceRef kind must be integer"))?;
        if kind != 0 && kind != 1 {
            return Err(malformed("EVIDENCE_REFERENCE_MALFORMED", "unsupported EvidenceRef kind"));
        }
        let bytes = parse_bytes(&a[1], "EVIDENCE_REFERENCE_MALFORMED")?;
        let digest: [u8; 32] = bytes
            .try_into()
            .map_err(|_| malformed("EVIDENCE_REFERENCE_MALFORMED", "identity digest must contain 32 octets"))?;
        Ok(Self { kind, digest })
    }
    fn canonical(&self) -> Result<Vec<u8>, OlpError> {
        cbor::encode(&Value::Array(vec![
            Value::Int(self.kind as i128),
            Value::Bytes(self.digest.to_vec()),
        ]))
        .map_err(|e| malformed("EVIDENCE_REFERENCE_MALFORMED", e))
    }
    fn json(&self) -> Json {
        let mut out = Json::object();
        out.insert("kind".into(), Json::Int(self.kind as i128));
        out.insert("identity_digest_hex".into(), Json::String(hex_encode(&self.digest)));
        Json::Object(out)
    }
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct ResourceRef {
    resource_id: Option<String>,
    media_type: String,
    algorithm: i64,
    digest: [u8; 32],
}
impl ResourceRef {
    fn parse(v: &Json) -> Result<Self, OlpError> {
        let a = v
            .as_array()
            .map_err(|_| malformed("MALFORMED_RESOURCE_REF", "ResourceRefV1 must be array"))?;
        if a.len() != 4 {
            return Err(malformed("MALFORMED_RESOURCE_REF", "ResourceRefV1 must contain four elements"));
        }
        let resource_id = match &a[0] {
            Json::Null => None,
            Json::String(s) if is_absolute_uri(s) => Some(s.clone()),
            _ => return Err(malformed("MALFORMED_RESOURCE_REF", "resource id must be absolute URI or null")),
        };
        let media_type = a[1]
            .as_str()
            .map_err(|_| malformed("MALFORMED_RESOURCE_REF", "media type must be text"))?
            .to_string();
        if !valid_media_type(&media_type) {
            return Err(malformed("MALFORMED_RESOURCE_REF", "invalid media type"));
        }
        let algorithm = a[2]
            .as_i64()
            .map_err(|_| malformed("MALFORMED_RESOURCE_REF", "hash algorithm must be integer"))?;
        if algorithm != -16 {
            return Err(unsupported("UNSUPPORTED_RESOURCE_HASH_ALGORITHM", "unsupported resource hash algorithm"));
        }
        let bytes = parse_bytes(&a[3], "MALFORMED_RESOURCE_REF")?;
        let digest: [u8; 32] = bytes
            .try_into()
            .map_err(|_| malformed("MALFORMED_RESOURCE_REF", "resource digest must contain 32 octets"))?;
        Ok(Self { resource_id, media_type, algorithm, digest })
    }
    fn canonical(&self) -> Result<Vec<u8>, OlpError> {
        cbor::encode(&Value::Array(vec![
            self.resource_id.as_ref().map(|v| Value::Text(v.clone())).unwrap_or(Value::Null),
            Value::Text(self.media_type.clone()),
            Value::Int(self.algorithm as i128),
            Value::Bytes(self.digest.to_vec()),
        ]))
        .map_err(|e| malformed("MALFORMED_RESOURCE_REF", e))
    }
    fn json(&self) -> Json {
        let mut out = Json::object();
        out.insert(
            "resource_id".into(),
            self.resource_id.as_ref().map(|v| Json::String(v.clone())).unwrap_or(Json::Null),
        );
        out.insert("media_type".into(), Json::String(self.media_type.clone()));
        out.insert("hash_algorithm".into(), Json::Int(self.algorithm as i128));
        out.insert("digest_hex".into(), Json::String(hex_encode(&self.digest)));
        Json::Object(out)
    }
}

fn valid_media_type(value: &str) -> bool {
    let mut parts = value.split('/');
    let left = parts.next().unwrap_or("");
    let right = parts.next().unwrap_or("");
    if left.is_empty() || right.is_empty() || parts.next().is_some() {
        return false;
    }
    fn part_ok(value: &str) -> bool {
        value.bytes().all(|c| c.is_ascii_lowercase() || c.is_ascii_digit() || b"!#$&^_.+-".contains(&c))
    }
    part_ok(left) && part_ok(right)
}

#[derive(Clone, Debug)]
struct Request {
    purpose: Option<String>,
    roots: Vec<EvidenceRef>,
    required_capabilities: Vec<String>,
    prefer_offline: bool,
    max_bundle_bytes: Option<u64>,
    permit_external: bool,
}

fn parse_options(v: &Json) -> Result<(bool, bool, Option<u64>, bool), OlpError> {
    let object = v
        .as_object()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "options must use adapter map projection"))?;
    let entries = object
        .get("$map")
        .ok_or_else(|| malformed("MALFORMED_DISCLOSURE_REQUEST", "options must use adapter $map projection"))?
        .as_array()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "$map must contain entries"))?;
    if object.len() != 1 {
        return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "invalid options wrapper"));
    }
    let mut minimal = false;
    let mut offline = false;
    let mut max_bytes = None;
    let mut external = false;
    let mut seen = BTreeSet::new();
    for entry in entries {
        let pair = entry
            .as_array()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "option entry must be pair"))?;
        if pair.len() != 2 {
            return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "option entry must be pair"));
        }
        let label = pair[0]
            .as_i64()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "option label must be integer"))?;
        if !seen.insert(label) {
            return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "duplicate disclosure option"));
        }
        match label {
            0 => minimal = pair[1].as_bool().map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "preferMinimalDisclosure must be boolean"))?,
            1 => offline = pair[1].as_bool().map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "preferOfflineVerification must be boolean"))?,
            2 => {
                max_bytes = match &pair[1] {
                    Json::Null => None,
                    value => Some(value.as_u64().map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "maxBundleBytes must be non-negative integer or null"))?),
                }
            }
            3 => external = pair[1].as_bool().map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "permitExternalNativePresentations must be boolean"))?,
            _ => return Err(unsupported("UNSUPPORTED_DISCLOSURE_OPTION", "unsupported disclosure option")),
        }
    }
    Ok((minimal, offline, max_bytes, external))
}

fn parse_request(v: &Json) -> Result<Request, OlpError> {
    let a = v
        .as_array()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "DisclosureRequestV1 must be array"))?;
    if a.len() != 8 {
        return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "DisclosureRequestV1 must contain eight elements"));
    }
    if a[0].as_str().ok() != Some(DOMAIN) {
        return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "invalid disclosure-request discriminator"));
    }
    let version = a[1]
        .as_i64()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "disclosure-request version must be integer"))?;
    if version != VERSION {
        return Err(unsupported("UNSUPPORTED_DISCLOSURE_REQUEST_VERSION", "unsupported disclosure-request version"));
    }
    let purpose = match &a[2] {
        Json::Null => None,
        Json::String(s) if is_absolute_uri(s) => Some(s.clone()),
        _ => return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "purpose must be absolute URI or null")),
    };
    let roots_raw = a[3]
        .as_array()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "roots must be array"))?;
    if roots_raw.is_empty() {
        return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "roots must be non-empty"));
    }
    let mut roots = Vec::new();
    let mut root_seen = BTreeSet::new();
    for raw in roots_raw {
        let reference = EvidenceRef::parse(raw)?;
        if !root_seen.insert(reference.clone()) {
            return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "roots must be unique"));
        }
        roots.push(reference);
    }
    let caps_raw = a[4]
        .as_array()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "requiredCapabilities must be array"))?;
    let mut caps = Vec::new();
    let mut cap_seen = BTreeSet::new();
    for raw in caps_raw {
        let cap = raw
            .as_str()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_REQUEST", "capability must be text"))?;
        if !is_semantic_identifier(cap) || !cap_seen.insert(cap.to_string()) {
            return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "invalid required capability set"));
        }
        caps.push(cap.to_string());
    }
    let mut sorted_caps = caps.clone();
    sorted_caps.sort_by(|a, b| a.as_bytes().cmp(b.as_bytes()));
    if caps != sorted_caps {
        return Err(malformed("MALFORMED_DISCLOSURE_REQUEST", "requiredCapabilities must be canonically sorted"));
    }
    let (_, prefer_offline, max_bundle_bytes, permit_external) = parse_options(&a[7])?;
    Ok(Request { purpose, roots, required_capabilities: caps, prefer_offline, max_bundle_bytes, permit_external })
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
enum Target {
    Evidence(EvidenceRef),
    Resource(ResourceRef),
}
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Dependency {
    target: Target,
    class: String,
}
impl Dependency {
    fn parse(v: &Json) -> Result<Self, OlpError> {
        let a = v
            .as_array()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "dependency must be array"))?;
        if a.len() != 3 {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "dependency must contain three elements"));
        }
        let target_class = a[0]
            .as_str()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "dependency target class must be text"))?;
        let class = a[2]
            .as_str()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "dependency class must be text"))?;
        if !matches!(class, "protocol" | "policy" | "offline") {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "unsupported disclosure dependency class"));
        }
        let target = match target_class {
            "evidence" => Target::Evidence(EvidenceRef::parse(&a[1])?),
            "resource" => Target::Resource(ResourceRef::parse(&a[1])?),
            _ => return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "unsupported dependency target class")),
        };
        Ok(Self { target, class: class.into() })
    }
    fn json(&self) -> Json {
        let mut out = Json::object();
        match &self.target {
            Target::Evidence(reference) => {
                out.insert("target_class".into(), Json::String("evidence".into()));
                out.insert("target".into(), reference.json());
            }
            Target::Resource(reference) => {
                out.insert("target_class".into(), Json::String("resource".into()));
                out.insert("target".into(), reference.json());
            }
        }
        out.insert("dependency_class".into(), Json::String(self.class.clone()));
        Json::Object(out)
    }
}

#[derive(Clone, Debug)]
struct EvidenceItem {
    reference: EvidenceRef,
    record_body: Option<Json>,
    proof_body: Option<Json>,
    dependencies: Vec<Dependency>,
    warnings: BTreeSet<String>,
}
impl EvidenceItem {
    fn parse(v: &Json) -> Result<Self, OlpError> {
        let o = v
            .as_object()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "inventory item must be map"))?;
        let reference = EvidenceRef::parse(o.get("ref").ok_or_else(|| malformed("MALFORMED_DISCLOSURE_INPUT", "missing ref"))?)?;
        let record_body = o.get("record").cloned();
        let proof_body = o.get("proof").cloned();
        if record_body.is_some() && proof_body.is_some() {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "inventory item cannot contain record and proof bodies"));
        }
        if record_body.is_some() && reference.kind != 0 {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "record body does not match evidence kind"));
        }
        if proof_body.is_some() && reference.kind != 1 {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "proof body does not match evidence kind"));
        }
        let mut dependencies = Vec::new();
        if let Some(raw) = o.get("dependencies") {
            for dep in raw
                .as_array()
                .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "dependencies must be array"))?
            {
                dependencies.push(Dependency::parse(dep)?);
            }
            let mut sorted = dependencies.clone();
            sorted.sort();
            sorted.dedup();
            if sorted.len() != dependencies.len() {
                return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "duplicate disclosure dependency"));
            }
        }
        let warnings = parse_warning_set(o.get("privacy_warnings"))?;
        Ok(Self { reference, record_body, proof_body, dependencies, warnings })
    }
    fn identity_valid(&self) -> Result<bool, OlpError> {
        if let Some(record_json) = &self.record_body {
            return Ok(record::identity_digest(record_json)? == self.reference.digest);
        }
        if let Some(proof_json) = &self.proof_body {
            return Ok(proof_identity::proof_identity_digest_for(proof_json)? == self.reference.digest);
        }
        Ok(true)
    }
}

#[derive(Clone, Debug)]
struct ResourceItem {
    reference: ResourceRef,
    content: Option<Vec<u8>>,
    native: bool,
    warnings: BTreeSet<String>,
}
impl ResourceItem {
    fn parse(v: &Json) -> Result<Self, OlpError> {
        let o = v
            .as_object()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "resource inventory item must be map"))?;
        let reference = ResourceRef::parse(o.get("ref").ok_or_else(|| malformed("MALFORMED_DISCLOSURE_INPUT", "missing resource ref"))?)?;
        let content = match o.get("content_hex") {
            None => None,
            Some(raw) => Some(hex_decode(raw.as_str().map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "content_hex must be text"))?)
                .map_err(|e| malformed("MALFORMED_DISCLOSURE_INPUT", e))?),
        };
        let native = match o.get("native_presentation") {
            None => false,
            Some(raw) => raw.as_bool().map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "native_presentation must be boolean"))?,
        };
        let warnings = parse_warning_set(o.get("privacy_warnings"))?;
        Ok(Self { reference, content, native, warnings })
    }
    fn identity_valid(&self) -> bool {
        self.content.as_ref().is_none_or(|content| sha256::digest(content) == self.reference.digest)
    }
}

fn parse_warning_set(value: Option<&Json>) -> Result<BTreeSet<String>, OlpError> {
    let Some(value) = value else { return Ok(BTreeSet::new()); };
    let a = value
        .as_array()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "privacy_warnings must be array"))?;
    let mut out = BTreeSet::new();
    for raw in a {
        let warning = raw
            .as_str()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "privacy warning must be text"))?;
        if !PRIVACY_WARNINGS.contains(&warning) {
            return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "unknown core privacy warning"));
        }
        out.insert(warning.to_string());
    }
    Ok(out)
}

fn record_warnings(record_json: &Json) -> BTreeSet<String> {
    let mut warnings = BTreeSet::new();
    let content = record_json
        .as_object()
        .ok()
        .and_then(|o| o.get("content"))
        .and_then(|v| v.as_array().ok());
    let Some(content) = content else { return warnings; };
    let Some(domain) = content.first().and_then(|v| v.as_str().ok()) else { return warnings; };
    if domain == "OLP-PRINCIPAL-RELATION" {
        warnings.insert("STABLE_PRINCIPAL_CORRELATION".into());
        if content.get(2).and_then(|v| v.as_str().ok()) == Some("controlsVerificationMethod") {
            warnings.insert("STABLE_VERIFICATION_METHOD_CORRELATION".into());
        }
        if content.get(2).and_then(|v| v.as_str().ok()) == Some("sameSubjectAs") {
            warnings.insert("SAME_SUBJECT_LINK_DISCLOSED".into());
        }
    } else if domain == "OLP-AUTHORITY-GRANT" {
        warnings.insert("STABLE_PRINCIPAL_CORRELATION".into());
    } else if domain == "OLP-LIFECYCLE-STATUS" {
        if let Some(target) = content.get(2).and_then(|v| v.as_array().ok()) {
            match target.first().and_then(|v| v.as_str().ok()) {
                Some("principal") => { warnings.insert("STABLE_PRINCIPAL_CORRELATION".into()); }
                Some("verificationMethod") => { warnings.insert("STABLE_VERIFICATION_METHOD_CORRELATION".into()); }
                _ => {}
            }
        }
    }
    warnings
}

fn json_strings(values: &BTreeSet<String>) -> Json {
    Json::Array(values.iter().cloned().map(Json::String).collect())
}

pub fn plan_operation(input: &Json) -> Result<Json, OlpError> {
    let payload = input
        .as_object()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "planner input must be map"))?;
    let request = parse_request(payload.get("request").ok_or_else(|| malformed("MALFORMED_DISCLOSURE_INPUT", "missing request"))?)?;

    let mut evidence = BTreeMap::<EvidenceRef, EvidenceItem>::new();
    if let Some(raw) = payload.get("inventory") {
        for entry in raw
            .as_array()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "inventory must be array"))?
        {
            let item = EvidenceItem::parse(entry)?;
            if evidence.insert(item.reference.clone(), item).is_some() {
                return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "duplicate evidence inventory reference"));
            }
        }
    }
    let mut resources = BTreeMap::<ResourceRef, ResourceItem>::new();
    if let Some(raw) = payload.get("resources") {
        for entry in raw
            .as_array()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "resources must be array"))?
        {
            let item = ResourceItem::parse(entry)?;
            if resources.insert(item.reference.clone(), item).is_some() {
                return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "duplicate resource inventory reference"));
            }
        }
    }

    let manifested = payload.get("manifested").map(|v| v.as_bool()).transpose()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "manifested must be boolean"))?.unwrap_or(true);
    let network_planned = payload.get("network_resolution_planned").map(|v| v.as_bool()).transpose()
        .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "network_resolution_planned must be boolean"))?.unwrap_or(false);

    let mut privacy = BTreeSet::<String>::new();
    privacy.insert("GLOBAL_COMPLETENESS_NOT_ESTABLISHED".into());
    if manifested { privacy.insert("BUNDLE_MANIFEST_CORRELATION".into()); }
    if network_planned { privacy.insert("NETWORK_RESOLUTION_LEAKAGE".into()); }
    let mut policy = BTreeSet::<String>::new();
    if request.max_bundle_bytes.is_some() {
        policy.insert("MAX_BUNDLE_BYTES_REQUIRES_PACKAGING_CHECK".into());
    }
    let mut errors = BTreeSet::<String>::new();
    if let Some(raw) = payload.get("available_capabilities") {
        let mut available = BTreeSet::new();
        for item in raw
            .as_array()
            .map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "available_capabilities must be array"))?
        {
            let text = item.as_str().map_err(|_| malformed("MALFORMED_DISCLOSURE_INPUT", "capability must be text"))?;
            if !is_semantic_identifier(text) { return Err(malformed("MALFORMED_DISCLOSURE_INPUT", "invalid available capability")); }
            available.insert(text.to_string());
        }
        if request.required_capabilities.iter().any(|cap| !available.contains(cap)) {
            errors.insert("REQUIRED_CAPABILITY_UNAVAILABLE".into());
        }
    }

    let roots_set: BTreeSet<EvidenceRef> = request.roots.iter().cloned().collect();
    let mut queue: VecDeque<EvidenceRef> = request.roots.iter().cloned().collect();
    let mut selected = BTreeMap::<EvidenceRef, EvidenceItem>::new();
    let mut selected_resources = BTreeMap::<ResourceRef, ResourceItem>::new();
    let mut unresolved = BTreeSet::<Dependency>::new();
    let mut policy_blocked = false;
    let mut offline_selected = false;

    while let Some(reference) = queue.pop_front() {
        if selected.contains_key(&reference) { continue; }
        let Some(item) = evidence.get(&reference).cloned() else {
            unresolved.insert(Dependency { target: Target::Evidence(reference.clone()), class: "protocol".into() });
            if roots_set.contains(&reference) { errors.insert("ROOT_NOT_AVAILABLE".into()); }
            continue;
        };
        if !item.identity_valid()? {
            errors.insert("EVIDENCE_IDENTITY_MISMATCH".into());
            continue;
        }
        privacy.extend(item.warnings.iter().cloned());
        if let Some(record_json) = &item.record_body { privacy.extend(record_warnings(record_json)); }
        if item.proof_body.is_some() { privacy.insert("STABLE_VERIFICATION_METHOD_CORRELATION".into()); }
        for dependency in &item.dependencies {
            if dependency.class == "offline" && !request.prefer_offline { continue; }
            if dependency.class == "offline" { offline_selected = true; }
            match &dependency.target {
                Target::Evidence(target) => {
                    if evidence.contains_key(target) { queue.push_back(target.clone()); }
                    else { unresolved.insert(dependency.clone()); }
                }
                Target::Resource(target) => {
                    let Some(resource) = resources.get(target).cloned() else { unresolved.insert(dependency.clone()); continue; };
                    if resource.native && !request.permit_external {
                        policy_blocked = true;
                        errors.insert("EXTERNAL_NATIVE_PRESENTATION_NOT_PERMITTED".into());
                        continue;
                    }
                    if !resource.identity_valid() {
                        errors.insert("RESOURCE_DIGEST_MISMATCH".into());
                        continue;
                    }
                    privacy.extend(resource.warnings.iter().cloned());
                    if resource.native { privacy.insert("EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN".into()); }
                    selected_resources.insert(target.clone(), resource);
                }
            }
        }
        selected.insert(reference, item);
    }
    if offline_selected { privacy.insert("SELF_CONTAINED_OVERDISCLOSURE".into()); }

    let status = if policy_blocked {
        "POLICY_BLOCKED"
    } else if errors.contains("REQUIRED_CAPABILITY_UNAVAILABLE") {
        "UNSUPPORTED"
    } else if errors.iter().any(|e| matches!(e.as_str(), "ROOT_NOT_AVAILABLE" | "EVIDENCE_IDENTITY_MISMATCH" | "RESOURCE_DIGEST_MISMATCH")) {
        "UNSATISFIABLE"
    } else if !unresolved.is_empty() {
        "PARTIAL"
    } else {
        "READY"
    };

    let mut roots: Vec<EvidenceRef> = request.roots.iter().filter(|r| selected.contains_key(*r)).cloned().collect();
    roots.sort_by_key(|r| r.canonical().unwrap_or_default());
    let mut selected_refs: Vec<EvidenceRef> = selected.keys().cloned().collect();
    selected_refs.sort_by_key(|r| r.canonical().unwrap_or_default());
    let mut resource_refs: Vec<ResourceRef> = selected_resources.keys().cloned().collect();
    resource_refs.sort_by_key(|r| r.canonical().unwrap_or_default());

    let mut out = Json::object();
    out.insert("status".into(), Json::String(status.into()));
    out.insert("purpose".into(), request.purpose.map(Json::String).unwrap_or(Json::Null));
    out.insert("selected_roots".into(), Json::Array(roots.iter().map(EvidenceRef::json).collect()));
    out.insert("selected_evidence".into(), Json::Array(selected_refs.iter().map(EvidenceRef::json).collect()));
    out.insert("selected_resources".into(), Json::Array(resource_refs.iter().map(ResourceRef::json).collect()));
    out.insert("unresolved_dependencies".into(), Json::Array(unresolved.iter().map(Dependency::json).collect()));
    out.insert("privacy_warnings".into(), json_strings(&privacy));
    out.insert("policy_warnings".into(), json_strings(&policy));
    out.insert("produced_bundle_id".into(), Json::Null);
    out.insert("errors".into(), json_strings(&errors));
    out.insert("disclosure_claim".into(), Json::String("TASK_SCOPED_MINIMIZED_DISCLOSURE".into()));
    out.insert("global_completeness_established".into(), Json::Bool(false));
    out.insert("field_redaction_performed".into(), Json::Bool(false));
    Ok(Json::Object(out))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn missing_root_never_becomes_absent_global_evidence() {
        let input = crate::json::parse(&format!(
            r#"{{"request":["OLP-DISCLOSURE-REQUEST",1,"urn:example:purpose:verify",[[0,{{"$bytes":"{}"}}]],[],{{}},{{}},{{"$map":[]}}],"inventory":[],"manifested":false}}"#,
            "11".repeat(32)
        )).unwrap();
        let result = plan_operation(&input).unwrap();
        assert_eq!(result.get("status").unwrap().as_str().unwrap(), "UNSATISFIABLE");
        assert_eq!(result.get("global_completeness_established").unwrap().as_bool().unwrap(), false);
    }

    #[test]
    fn planner_never_reports_field_redaction() {
        let input = crate::json::parse(&format!(
            r#"{{"request":["OLP-DISCLOSURE-REQUEST",1,null,[[1,{{"$bytes":"{}"}}]],[],{{}},{{}},{{"$map":[]}}],"inventory":[{{"ref":[1,{{"$bytes":"{}"}}]}}],"manifested":false}}"#,
            "22".repeat(32), "22".repeat(32)
        )).unwrap();
        let result = plan_operation(&input).unwrap();
        assert_eq!(result.get("field_redaction_performed").unwrap().as_bool().unwrap(), false);
    }
}
