from __future__ import annotations

from dataclasses import replace

import pytest

from conftest import TEST_METHOD, load_vector
from olp.constants import MANDATORY_CRYPTOSUITE
from olp.crypto.proof import create_proof
from olp.encoding.proof_input import proof_input_bytes
from olp.errors import ConformanceError, UnsupportedFeatureError


def test_end_to_end_reference_vector(sample_record, test_seed):
    vector = load_vector("milestone13-end-to-end-v1.json")
    proof = create_proof(
        sample_record,
        proof_purpose=vector["proof_configuration"]["proof_purpose"],
        verification_method=vector["proof_configuration"]["verification_method"],
        private_key=test_seed,
    )
    assert proof.recordCommitment.algorithm == -16
    assert proof.recordCommitment.digest.hex() == vector["expected"]["record_commitment_digest_hex"]
    assert proof_input_bytes(proof).hex() == vector["expected"]["proof_input_hex"]
    assert proof.proofValue.hex() == vector["expected"]["proof_value_hex"]


def test_proof_creation_is_deterministic_without_changing_authenticated_inputs(sample_record, test_seed):
    a = create_proof(sample_record, proof_purpose="assertion", verification_method=TEST_METHOD, private_key=test_seed)
    b = create_proof(sample_record, proof_purpose="assertion", verification_method=TEST_METHOD, private_key=test_seed)
    assert a == b


def test_created_is_authenticated_and_changes_signature(sample_record, test_seed):
    a = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        created="2026-08-20T00:00:00Z",
    )
    b = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        created="2026-08-20T00:00:01Z",
    )
    assert a.proofValue != b.proofValue


def test_extension_and_critical_are_authenticated(sample_record, test_seed):
    extension = "https://example.org/olp/limit"
    proof = create_proof(
        sample_record,
        proof_purpose="authorization",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        extensions={extension: 5000},
        critical=(extension,),
    )
    assert extension in proof.extensions
    assert proof.critical == (extension,)


def test_invalid_created_rejected_before_signing(sample_record, test_seed):
    with pytest.raises(ConformanceError):
        create_proof(
            sample_record,
            proof_purpose="assertion",
            verification_method=TEST_METHOD,
            private_key=test_seed,
            created="not-a-time",
        )


def test_invalid_verification_method_rejected_before_signing(sample_record, test_seed):
    with pytest.raises(ConformanceError):
        create_proof(
            sample_record,
            proof_purpose="assertion",
            verification_method="relative/key",
            private_key=test_seed,
        )


def test_missing_critical_extension_rejected(sample_record, test_seed):
    with pytest.raises(ConformanceError):
        create_proof(
            sample_record,
            proof_purpose="assertion",
            verification_method=TEST_METHOD,
            private_key=test_seed,
            critical=("https://example.org/missing",),
        )


def test_unsupported_cryptosuite_rejected_by_producer(sample_record, test_seed):
    with pytest.raises(UnsupportedFeatureError) as exc:
        create_proof(
            sample_record,
            proof_purpose="assertion",
            verification_method=TEST_METHOD,
            private_key=test_seed,
            cryptosuite="https://example.org/future-suite",
        )
    assert exc.value.code == "UNSUPPORTED_CRYPTOSUITE"


def test_unsupported_commitment_algorithm_rejected_by_producer(sample_record, test_seed):
    with pytest.raises(UnsupportedFeatureError) as exc:
        create_proof(
            sample_record,
            proof_purpose="assertion",
            verification_method=TEST_METHOD,
            private_key=test_seed,
            commitment_algorithm=-999,
        )
    assert exc.value.code == "UNSUPPORTED_COMMITMENT_ALGORITHM"


def test_proof_is_deeply_immutable(sample_record, test_seed):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        extensions={"https://example.org/context": {"a": 1}},
    )
    with pytest.raises(TypeError):
        proof.extensions["https://example.org/context"] = 2
    with pytest.raises(TypeError):
        proof.extensions["https://example.org/context"]["a"] = 2


def test_mandatory_suite_identifier_is_used(sample_record, test_seed):
    proof = create_proof(sample_record, proof_purpose="assertion", verification_method=TEST_METHOD, private_key=test_seed)
    assert proof.cryptosuite == MANDATORY_CRYPTOSUITE
