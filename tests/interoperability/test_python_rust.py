from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from olp_conformance.adapter import SubprocessAdapter
from olp_conformance.adapters.reference import ReferenceAdapter

ROOT = Path(__file__).resolve().parents[2]
RUST_MANIFEST = ROOT / "implementations" / "rust" / "Cargo.toml"
RUST_BINARY = ROOT / "implementations" / "rust" / "target" / "release" / "olp-conformance-adapter"
VECTOR_ROOT = ROOT / "conformance" / "vectors"

pytestmark = pytest.mark.skipif(
    os.environ.get("OLP_RUN_RUST_INTEROP") != "1",
    reason="set OLP_RUN_RUST_INTEROP=1 in the Rust interoperability job",
)


def _build_rust() -> Path:
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
    binary = _build_rust()
    return SubprocessAdapter([str(binary)], name="rust-independent")


def _vector(relative: str) -> dict:
    return json.loads((VECTOR_ROOT / relative).read_text(encoding="utf-8"))


def test_capabilities_match_reference(rust_adapter: SubprocessAdapter) -> None:
    assert rust_adapter.capabilities() == ReferenceAdapter().capabilities()


def test_record_identity_matches_python_and_spec(rust_adapter: SubprocessAdapter) -> None:
    case = _vector("record_identity/positive/record-identity-spec-vector-001.json")
    payload = case["input"]
    py = ReferenceAdapter().execute("derive_record_identity", payload)
    rs = rust_adapter.execute("derive_record_identity", payload)
    assert rs == py
    assert rs == case["expected"]["result"]


def test_proof_input_matches_python_and_spec(rust_adapter: SubprocessAdapter) -> None:
    case = _vector("proof_input/positive/proof-input-spec-vector-001.json")
    payload = case["input"]
    py = ReferenceAdapter().execute("encode_proof_input", payload)
    rs = rust_adapter.execute("encode_proof_input", payload)
    assert rs == py
    assert rs == case["expected"]["result"]


def test_rust_and_python_create_identical_deterministic_proof(rust_adapter: SubprocessAdapter) -> None:
    case = _vector("proof_creation/positive/proof-create-end-to-end-001.json")
    payload = case["input"]
    py = ReferenceAdapter().execute("create_proof", payload)
    rs = rust_adapter.execute("create_proof", payload)
    assert rs == py
    assert rs == case["expected"]["result"]


def test_python_created_proof_verifies_in_rust(rust_adapter: SubprocessAdapter) -> None:
    create_case = _vector("proof_creation/positive/proof-create-end-to-end-001.json")
    verify_case = _vector("proof_verification/positive/proof-verify-valid-001.json")
    created = ReferenceAdapter().execute("create_proof", create_case["input"])["proof"]
    payload = dict(verify_case["input"])
    payload["proof"] = created
    result = rust_adapter.execute("verify_proof", payload)
    assert result["cryptographic_validity"] == "VALID"
    assert result["record_binding"] == "VALID"


def test_rust_created_proof_verifies_in_python(rust_adapter: SubprocessAdapter) -> None:
    create_case = _vector("proof_creation/positive/proof-create-end-to-end-001.json")
    verify_case = _vector("proof_verification/positive/proof-verify-valid-001.json")
    created = rust_adapter.execute("create_proof", create_case["input"])["proof"]
    payload = dict(verify_case["input"])
    payload["proof"] = created
    result = ReferenceAdapter().execute("verify_proof", payload)
    assert result["cryptographic_validity"] == "VALID"
    assert result["record_binding"] == "VALID"


def test_proof_identity_matches_python_and_spec(rust_adapter: SubprocessAdapter) -> None:
    case = _vector("proof_identity/positive/proof-identity-spec5-001.json")
    payload = case["input"]
    py = ReferenceAdapter().execute("derive_proof_identity", payload)
    rs = rust_adapter.execute("derive_proof_identity", payload)
    assert rs == py
    assert rs == case["expected"]["result"]


def test_evidence_refs_match_python_and_spec(rust_adapter: SubprocessAdapter) -> None:
    for relative in (
        "evidence_ref/positive/evidence-ref-record-001.json",
        "evidence_ref/positive/evidence-ref-proof-001.json",
    ):
        case = _vector(relative)
        py = ReferenceAdapter().execute("encode_evidence_ref", case["input"])
        rs = rust_adapter.execute("encode_evidence_ref", case["input"])
        assert rs == py == case["expected"]["result"]


def test_relationship_processing_matches_python_and_spec(rust_adapter: SubprocessAdapter) -> None:
    for relative in (
        "evidence_relationship/positive/relationship-references-001.json",
        "evidence_relationship/positive/relationship-countersigns-001.json",
    ):
        case = _vector(relative)
        py = ReferenceAdapter().execute("process_relationship", case["input"])
        rs = rust_adapter.execute("process_relationship", case["input"])
        assert rs == py == case["expected"]["result"]
