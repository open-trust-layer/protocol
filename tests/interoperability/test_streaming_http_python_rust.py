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
VECTOR_ROOT = ROOT / "conformance" / "vectors" / "streaming-http"

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
            assert key in observed, f"{path}: missing {key!r}"
            _assert_subset(value, observed[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        assert isinstance(observed, list), f"{path}: expected list"
        assert len(expected) == len(observed), f"{path}: list length differs"
        for index, (expected_item, observed_item) in enumerate(zip(expected, observed)):
            _assert_subset(expected_item, observed_item, f"{path}[{index}]")
        return
    assert observed == expected, f"{path}: expected {expected!r}, observed {observed!r}"


def _compare_vector(rust_adapter, relative: str):
    case = _vector(relative)
    py = ReferenceAdapter().execute(case["operation"], case["input"])
    rs = rust_adapter.execute(case["operation"], case["input"])
    expected = case["expected"]["result"]
    _assert_subset(expected, py)
    _assert_subset(expected, rs)
    return py, rs


def test_stream_frame_and_sequence_wire_bytes_match_exactly(rust_adapter):
    frame_py, frame_rs = _compare_vector(rust_adapter, "positive/stream-frame-wire-001.json")
    assert frame_rs["json_seq_hex"] == frame_py["json_seq_hex"]
    assert frame_rs["cbor_item_hex"] == frame_py["cbor_item_hex"]

    sequence_py, sequence_rs = _compare_vector(rust_adapter, "positive/stream-sequence-wire-001.json")
    assert sequence_rs["frame_count"] == sequence_py["frame_count"]
    assert sequence_rs["json_seq_hex"] == sequence_py["json_seq_hex"]
    assert sequence_rs["cbor_seq_hex"] == sequence_py["cbor_seq_hex"]


def test_stream_semantic_separations_match(rust_adapter):
    for relative in (
        "positive/stream-order-record-resource-001.json",
        "positive/stream-order-resource-record-001.json",
        "negative/stream-truncated-001.json",
        "negative/stream-invalid-resource-complete-001.json",
    ):
        py, rs = _compare_vector(rust_adapter, relative)
        assert rs["transport_status"] == py["transport_status"], relative
        assert rs["bundle"]["status"] == py["bundle"]["status"], relative


def test_http_identity_status_and_semantic_status_match(rust_adapter):
    for relative in (
        "positive/http-read-record-001.json",
        "negative/http-read-identity-mismatch-001.json",
        "negative/http-read-local-not-found-001.json",
        "positive/http-resolution-not-found-001.json",
    ):
        _compare_vector(rust_adapter, relative)


def test_http_digest_and_redirect_policy_match(rust_adapter):
    for relative in (
        "positive/http-content-digest-valid-001.json",
        "negative/http-content-digest-mismatch-001.json",
        "negative/http-redirect-https-downgrade-001.json",
        "negative/http-redirect-identity-change-001.json",
        "positive/http-redirect-cross-origin-no-creds-001.json",
    ):
        _compare_vector(rust_adapter, relative)


def test_http_auth_cache_range_and_limits_match(rust_adapter):
    for relative in (
        "positive/http-auth-proof-separated-001.json",
        "positive/http-cache-representation-specific-001.json",
        "negative/http-cache-sensitive-public-001.json",
        "negative/http-range-partial-001.json",
        "negative/http-limit-413-001.json",
        "negative/http-rate-limit-429-001.json",
    ):
        _compare_vector(rust_adapter, relative)
