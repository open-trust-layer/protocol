from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from olp_conformance.adapter import SubprocessAdapter
from olp_conformance.adapters import ReferenceAdapter

ROOT = Path(__file__).resolve().parents[2]
RUST_MANIFEST = ROOT / "implementations" / "rust" / "Cargo.toml"
RUST_BINARY = ROOT / "implementations" / "rust" / "target" / "release" / "olp-conformance-adapter"
VECTOR_ROOT = ROOT / "conformance" / "vectors"

pytestmark = pytest.mark.skipif(
    os.environ.get("OLP_RUN_RUST_INTEROP") != "1",
    reason="set OLP_RUN_RUST_INTEROP=1 in the Rust interoperability job",
)


def _build_rust() -> Path:
    if not RUST_BINARY.exists():
        if shutil.which("cargo") is None:
            pytest.skip("cargo is not installed")
        subprocess.run(
            ["cargo", "build", "--release", "--locked", "--manifest-path", str(RUST_MANIFEST)],
            cwd=ROOT,
            check=True,
        )
    assert RUST_BINARY.exists()
    return RUST_BINARY


@pytest.fixture(scope="session")
def rust_adapter() -> SubprocessAdapter:
    return SubprocessAdapter([str(_build_rust())], name="rust-independent")


def _vector(relative: str) -> dict:
    return json.loads((VECTOR_ROOT / relative).read_text(encoding="utf-8"))


def _assert_subset(expected, observed, path="$"):
    if isinstance(expected, dict):
        assert isinstance(observed, dict), f"{path}: expected object"
        for key, value in expected.items():
            assert key in observed, f"{path}: missing key {key!r}"
            _assert_subset(value, observed[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        assert isinstance(observed, list), f"{path}: expected list"
        assert len(expected) == len(observed), f"{path}: list length differs"
        for index, (expected_item, observed_item) in enumerate(zip(expected, observed)):
            _assert_subset(expected_item, observed_item, f"{path}[{index}]")
        return
    assert observed == expected, f"{path}: expected {expected!r}, observed {observed!r}"


def test_transport_scalar_ojve_and_envelope_match_exactly(rust_adapter):
    cases = (
        "transport-encoding/positive/transport-identity-record-001.json",
        "transport-encoding/positive/transport-ojve-map-keys-001.json",
        "transport-encoding/positive/transport-envelope-json-001.json",
    )
    for relative in cases:
        case = _vector(relative)
        py = ReferenceAdapter().execute(case["operation"], case["input"])
        rs = rust_adapter.execute(case["operation"], case["input"])
        assert rs == py, relative
        _assert_subset(case["expected"]["result"], rs)


def test_record_and_proof_transport_preserve_identity_and_cbor(rust_adapter):
    cases = (
        "transport-encoding/positive/transport-record-equivalence-001.json",
        "transport-encoding/positive/transport-proof-equivalence-001.json",
    )
    for relative in cases:
        case = _vector(relative)
        expected = case["expected"]["result"]
        py = ReferenceAdapter().execute(case["operation"], case["input"])
        rs = rust_adapter.execute(case["operation"], case["input"])

        # OJVE map entry order is explicitly non-semantic, so the complete JSON
        # convenience projection need not be byte-identical. The immutable
        # identities and deterministic CBOR transport bytes must be identical.
        _assert_subset(expected, py)
        _assert_subset(expected, rs)
        assert rs["cbor_hex"] == py["cbor_hex"] == expected["cbor_hex"], relative
        assert rs["identity_preserved"] is True
        assert py["identity_preserved"] is True


def test_transport_identity_decode_matches_python(rust_adapter):
    case = _vector("transport-encoding/positive/transport-identity-decode-001.json")
    py = ReferenceAdapter().execute(case["operation"], case["input"])
    rs = rust_adapter.execute(case["operation"], case["input"])
    assert rs == py == case["expected"]["result"]
