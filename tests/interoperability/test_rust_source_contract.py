from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
RUST = ROOT / "implementations" / "rust"


def test_rust_crate_is_present_and_dependency_free():
    manifest = tomllib.loads((RUST / "Cargo.toml").read_text(encoding="utf-8"))
    assert manifest["package"]["name"] == "open-layer-protocol-rust"
    assert manifest["package"]["rust-version"] == "1.85"
    assert manifest.get("dependencies", {}) == {}


def test_rust_adapter_and_normative_tests_are_present():
    assert (RUST / "src" / "bin" / "olp-conformance-adapter.rs").is_file()
    assert (RUST / "tests" / "normative_vectors.rs").is_file()


def test_rust_source_does_not_import_or_spawn_python_reference():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in sorted((RUST / "src").rglob("*.rs")))
    for token in ("src/olp", "olp_conformance", "python", "pyo3", "Command::new"):
        assert token not in combined


def test_rust_adapter_declares_all_core_v1_capabilities():
    source = (RUST / "src" / "lib.rs").read_text(encoding="utf-8")
    for capability in ("olp.record-identity.v1","olp.record-commitment.sha256.v1","olp.proof-input.v1","olp.proof.eddsa-ed25519.v1","olp.proof-verification.v1"):
        assert capability in source


def test_rust_build_output_is_ignored():
    assert "implementations/rust/target/" in (ROOT / ".gitignore").read_text(encoding="utf-8")


def test_rust_bundle_capability_is_wired():
    lib=(RUST/"src"/"lib.rs").read_text(encoding="utf-8"); bundle=(RUST/"src"/"bundle.rs").read_text(encoding="utf-8")
    assert "olp.bundle.v1" in lib; assert '"process_bundle"=>bundle::process_bundle_operation' in lib; assert "OLP-EVIDENCE-BUNDLE-MANIFEST" in bundle


def test_rust_resolution_capability_is_wired():
    lib=(RUST/"src"/"lib.rs").read_text(encoding="utf-8"); resolution=(RUST/"src"/"resolution.rs").read_text(encoding="utf-8")
    assert "olp.resolution.v1" in lib; assert '"resolve"=>resolution::resolve_operation' in lib; assert "OLP-RESOLUTION-REQUEST" in resolution; assert "NETWORK_ACCESS_DISABLED" in resolution


def test_rust_identity_authority_lifecycle_capability_is_wired_and_policy_separated():
    lib=(RUST/"src"/"lib.rs").read_text(encoding="utf-8")
    source=(RUST/"src"/"identity_authority_lifecycle.rs").read_text(encoding="utf-8")
    assert "olp.identity-authority-lifecycle.v1" in lib
    assert '"evaluate_authority_lifecycle"=>identity_authority_lifecycle::evaluate_operation' in lib
    for token in (
        "OLP-PRINCIPAL-RELATION",
        "OLP-AUTHORITY-GRANT",
        "OLP-AUTHORITY-STATUS",
        "OLP-LIFECYCLE-STATUS",
        "PARENT_GRANT_IDENTITY_MISMATCH",
        "STATUS_SEQUENCE_CONFLICT",
        '"INDETERMINATE"',
    ):
        assert token in source
    assert 'out.insert("authorized"' not in source


def test_rust_privacy_disclosure_capability_preserves_minimization_boundaries():
    lib=(RUST/"src"/"lib.rs").read_text(encoding="utf-8")
    source=(RUST/"src"/"disclosure.rs").read_text(encoding="utf-8")
    assert "olp.privacy-disclosure.v1" in lib
    assert '"plan_disclosure"=>disclosure::plan_operation' in lib
    for token in (
        "OLP-DISCLOSURE-REQUEST",
        "TASK_SCOPED_MINIMIZED_DISCLOSURE",
        "GLOBAL_COMPLETENESS_NOT_ESTABLISHED",
        "SELF_CONTAINED_OVERDISCLOSURE",
        "NETWORK_RESOLUTION_LEAKAGE",
        "EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN",
        "EVIDENCE_IDENTITY_MISMATCH",
        "RESOURCE_DIGEST_MISMATCH",
        "record::identity_digest",
        "proof_identity",
    ):
        assert token in source
    assert 'out.insert("global_completeness_established".into(), Json::Bool(false))' in source
    assert 'out.insert("field_redaction_performed".into(), Json::Bool(false))' in source


def test_rust_transport_encoding_preserves_typed_values_identity_and_cbor():
    lib=(RUST/"src"/"lib.rs").read_text(encoding="utf-8")
    source=(RUST/"src"/"transport.rs").read_text(encoding="utf-8")
    cbor_bridge=(RUST/"src"/"transport_cbor.rs").read_text(encoding="utf-8")
    proof_bridge=(RUST/"src"/"transport_proof.rs").read_text(encoding="utf-8")
    assert "olp.transport-encoding.v1" in lib
    assert "transport_cbor::encode_envelope" in lib
    assert "transport_cbor::record_equivalence" in lib
    for operation in (
        "encode_identity_text",
        "decode_identity_text",
        "encode_ojve",
        "decode_ojve",
        "encode_transport_envelope",
        "decode_transport_envelope",
        "transport_record_equivalence",
        "transport_proof_equivalence",
    ):
        assert operation in lib
    for token in (
        '"r1_"', '"p1_"', '"b1_"',
        "non-canonical base64url pad bits",
        "DUPLICATE_OJVE_MAP_KEY",
        "UNSUPPORTED_OJVE_TAG",
        "MALFORMED_TRANSPORT_ENVELOPE",
        "AValue::Bytes",
        "AValue::Int",
        "AValue::Text",
        "AValue::Map",
        "record::identity_digest",
    ):
        assert token in source
    for token in (
        "OLP-TRANSPORT",
        "cbor::from_adapter_json",
        "cbor::encode",
        "UNSUPPORTED_TRANSPORT_CBOR_VALUE",
        '"cbor_hex"',
    ):
        assert token in cbor_bridge
    assert "proof_identity::proof_identity_digest_for" in proof_bridge
    assert "transport_cbor::encode_envelope" in proof_bridge
    # M23 is deliberately non-network. The accepted source must not grow a
    # transport client/server or authorization surface under this capability.
    combined = source + "\n" + cbor_bridge + "\n" + proof_bridge
    for token in ("TcpStream", "UdpSocket", "reqwest", "hyper::", "std::net", "authorized"):
        assert token not in combined
