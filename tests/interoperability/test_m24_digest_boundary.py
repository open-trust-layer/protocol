from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUST = ROOT / "implementations" / "rust" / "src"
PYTHON = ROOT / "src"


def test_python_m24_adapter_uses_parsed_digest_semantics_not_raw_header_parser():
    adapter = (PYTHON / "olp_conformance" / "adapters" / "m24.py").read_text(encoding="utf-8")
    source = (PYTHON / "olp" / "content_digest.py").read_text(encoding="utf-8")
    assert "validate_parsed_content_digest" in adapter
    assert 'payload.get("digest_members")' in adapter
    assert "RFC 8941 Structured Fields" in source
    assert "already-parsed" in source
    assert "duplicate Content-Digest algorithm" in source
    assert "sha-256 Content-Digest must contain exactly 32 octets" in source
    assert "base64" not in source


def test_rust_adapter_routes_digest_validation_to_parsed_semantics_module():
    lib = (RUST / "lib.rs").read_text(encoding="utf-8")
    source = (RUST / "content_digest.rs").read_text(encoding="utf-8")
    assert '"validate_content_digest"=>content_digest::operation(input)' in lib
    assert "RFC 8941 Structured Fields parsing belongs to the HTTP stack" in source
    assert 'obj.get("digest_members")' in source
    assert "duplicate Content-Digest algorithm" in source
    assert "sha-256 Content-Digest must contain exactly 32 octets" in source
    for token in ("base64", "header_value", "StructuredFieldParser", "sfv"):
        assert token not in source
