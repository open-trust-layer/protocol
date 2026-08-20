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
    # A test may probe for the absence of an authorization field, but production
    # output construction must never synthesize one.
    assert 'out.insert("authorized"' not in source
