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
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((RUST / "src").rglob("*.rs"))
    )
    forbidden = ("src/olp", "olp_conformance", "python", "pyo3", "Command::new")
    for token in forbidden:
        assert token not in combined


def test_rust_adapter_declares_all_core_v1_capabilities():
    source = (RUST / "src" / "lib.rs").read_text(encoding="utf-8")
    for capability in (
        "olp.record-identity.v1",
        "olp.record-commitment.sha256.v1",
        "olp.proof-input.v1",
        "olp.proof.eddsa-ed25519.v1",
        "olp.proof-verification.v1",
    ):
        assert capability in source


def test_rust_build_output_is_ignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "implementations/rust/target/" in gitignore
