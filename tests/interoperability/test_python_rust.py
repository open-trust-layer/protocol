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

pytestmark = pytest.mark.skipif(os.environ.get("OLP_RUN_RUST_INTEROP") != "1", reason="set OLP_RUN_RUST_INTEROP=1 in the Rust interoperability job")

def _build_rust() -> Path:
    if shutil.which("cargo") is None: pytest.skip("cargo is not installed")
    subprocess.run(["cargo","build","--release","--locked","--manifest-path",str(RUST_MANIFEST)],cwd=ROOT,check=True)
    assert RUST_BINARY.exists(); return RUST_BINARY

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


def test_capabilities_match_reference(rust_adapter):
    assert rust_adapter.capabilities() == ReferenceAdapter().capabilities()

def test_record_identity_matches_python_and_spec(rust_adapter):
    case=_vector("record_identity/positive/record-identity-spec-vector-001.json"); py=ReferenceAdapter().execute("derive_record_identity",case["input"]); rs=rust_adapter.execute("derive_record_identity",case["input"]); assert rs==py==case["expected"]["result"]

def test_proof_input_matches_python_and_spec(rust_adapter):
    case=_vector("proof_input/positive/proof-input-spec-vector-001.json"); py=ReferenceAdapter().execute("encode_proof_input",case["input"]); rs=rust_adapter.execute("encode_proof_input",case["input"]); assert rs==py==case["expected"]["result"]

def test_rust_and_python_create_identical_deterministic_proof(rust_adapter):
    case=_vector("proof_creation/positive/proof-create-end-to-end-001.json"); py=ReferenceAdapter().execute("create_proof",case["input"]); rs=rust_adapter.execute("create_proof",case["input"]); assert rs==py==case["expected"]["result"]

def test_python_created_proof_verifies_in_rust(rust_adapter):
    c=_vector("proof_creation/positive/proof-create-end-to-end-001.json"); v=_vector("proof_verification/positive/proof-verify-valid-001.json"); created=ReferenceAdapter().execute("create_proof",c["input"])["proof"]; payload=dict(v["input"]); payload["proof"]=created; result=rust_adapter.execute("verify_proof",payload); assert result["cryptographic_validity"]=="VALID" and result["record_binding"]=="VALID"

def test_rust_created_proof_verifies_in_python(rust_adapter):
    c=_vector("proof_creation/positive/proof-create-end-to-end-001.json"); v=_vector("proof_verification/positive/proof-verify-valid-001.json"); created=rust_adapter.execute("create_proof",c["input"])["proof"]; payload=dict(v["input"]); payload["proof"]=created; result=ReferenceAdapter().execute("verify_proof",payload); assert result["cryptographic_validity"]=="VALID" and result["record_binding"]=="VALID"

def test_proof_identity_matches_python_and_spec(rust_adapter):
    case=_vector("proof_identity/positive/proof-identity-spec5-001.json"); py=ReferenceAdapter().execute("derive_proof_identity",case["input"]); rs=rust_adapter.execute("derive_proof_identity",case["input"]); assert rs==py==case["expected"]["result"]

def test_evidence_refs_match_python_and_spec(rust_adapter):
    for rel in ("evidence_ref/positive/evidence-ref-record-001.json","evidence_ref/positive/evidence-ref-proof-001.json"):
        case=_vector(rel); py=ReferenceAdapter().execute("encode_evidence_ref",case["input"]); rs=rust_adapter.execute("encode_evidence_ref",case["input"]); assert rs==py==case["expected"]["result"]

def test_relationship_processing_matches_python_and_spec(rust_adapter):
    for rel in ("evidence_relationship/positive/relationship-references-001.json","evidence_relationship/positive/relationship-countersigns-001.json"):
        case=_vector(rel); py=ReferenceAdapter().execute("process_relationship",case["input"]); rs=rust_adapter.execute("process_relationship",case["input"]); assert rs==py==case["expected"]["result"]

def test_bundle_processing_matches_python_and_spec(rust_adapter):
    for rel in ("bundle/positive/bundle-portable-valid-001.json","bundle/positive/bundle-resource-valid-001.json","bundle/negative/bundle-partial-missing-001.json"):
        case=_vector(rel); py=ReferenceAdapter().execute("process_bundle",case["input"]); rs=rust_adapter.execute("process_bundle",case["input"]); assert rs==py==case["expected"]["result"]

def test_resolution_processing_matches_python_and_spec(rust_adapter):
    for rel in ("resolution/positive/resolution-evidence-bundle-hit-001.json","resolution/positive/resolution-network-redirect-resolved-001.json","resolution/negative/resolution-network-private-address-001.json","resolution/negative/resolution-network-loop-001.json"):
        case=_vector(rel); py=ReferenceAdapter().execute("resolve",case["input"]); rs=rust_adapter.execute("resolve",case["input"]); assert rs==py==case["expected"]["result"]


def test_identity_authority_lifecycle_matches_python_and_vectors(rust_adapter):
    cases = (
        "identity-authority-lifecycle/positive/principal-role-separated-001.json",
        "identity-authority-lifecycle/positive/delegation-verified-001.json",
        "identity-authority-lifecycle/negative/delegation-identity-mismatch-001.json",
        "identity-authority-lifecycle/negative/delegation-scope-mismatch-001.json",
        "identity-authority-lifecycle/negative/lifecycle-sequence-conflict-001.json",
        "identity-authority-lifecycle/negative/lifecycle-stale-001.json",
    )
    for relative in cases:
        case = _vector(relative)
        py = ReferenceAdapter().execute("evaluate_authority_lifecycle", case["input"])
        rs = rust_adapter.execute("evaluate_authority_lifecycle", case["input"])
        assert rs == py, relative
        _assert_subset(case["expected"]["result"], rs)
