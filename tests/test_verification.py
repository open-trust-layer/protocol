from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from conftest import TEST_METHOD
from olp.crypto.proof import create_proof, verify_proof
from olp.model.proof import OLPProof, RecordCommitment
from olp.model.record import RecordV1
from olp.model.verification import (
    MethodStatus,
    ReasonCode,
    ResolvedVerificationMethod,
    Status,
    VerificationPolicy,
)


def codes(result):
    return {issue.code for issue in result.errors}


def warning_codes(result):
    return {issue.code for issue in result.warnings}


def test_valid_proof_verifies(sample_record, sample_proof, resolved_method):
    result = verify_proof(sample_record, sample_proof, resolved_method=resolved_method)
    assert result.conformance == Status.CONFORMING
    assert result.record_binding == Status.VALID
    assert result.version_support == Status.SUPPORTED
    assert result.cryptosuite_support == Status.SUPPORTED
    assert result.commitment_algorithm_support == Status.SUPPORTED
    assert result.verification_method_resolution == Status.RESOLVED
    assert result.verification_method_compatibility == Status.COMPATIBLE
    assert result.cryptographic_validity == Status.VALID
    assert result.purpose_status == Status.UNDERSTOOD
    assert result.errors == ()


def test_mutated_record_is_commitment_mismatch_and_signature_not_evaluated(sample_record, sample_proof, resolved_method):
    mutated = replace(sample_record, content={"subject": "urn:example:subject:1", "statement": "mutated"})
    result = verify_proof(mutated, sample_proof, resolved_method=resolved_method)
    assert result.record_binding == Status.INVALID
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.RECORD_COMMITMENT_MISMATCH in codes(result)


def test_mutated_purpose_with_same_signature_is_signature_invalid(sample_record, sample_proof, resolved_method):
    mutated = replace(sample_proof, proofPurpose="witness")
    result = verify_proof(sample_record, mutated, resolved_method=resolved_method)
    assert result.record_binding == Status.VALID
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)


def test_mutated_verification_method_cannot_reuse_signature(sample_record, sample_proof, resolved_method):
    other_id = "urn:example:olp:other-key"
    mutated = replace(sample_proof, verificationMethod=other_id)
    supplied = replace(resolved_method, identifier=other_id)
    result = verify_proof(sample_record, mutated, resolved_method=supplied)
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)


def test_verification_method_identifier_mismatch_stops_crypto(sample_record, sample_proof, resolved_method):
    supplied = replace(resolved_method, identifier="urn:example:olp:wrong")
    result = verify_proof(sample_record, sample_proof, resolved_method=supplied)
    assert result.verification_method_compatibility == Status.MISMATCH
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.VERIFICATION_METHOD_MISMATCH in codes(result)


def test_missing_verification_method_is_unavailable_not_invalid(sample_record, sample_proof):
    result = verify_proof(sample_record, sample_proof, resolved_method=None)
    assert result.verification_method_resolution == Status.UNAVAILABLE
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.VERIFICATION_METHOD_UNAVAILABLE in codes(result)
    assert ReasonCode.SIGNATURE_INVALID not in codes(result)


def test_incompatible_key_type_is_distinct(sample_record, sample_proof, resolved_method):
    supplied = replace(resolved_method, key_type="X25519")
    result = verify_proof(sample_record, sample_proof, resolved_method=supplied)
    assert result.verification_method_compatibility == Status.INCOMPATIBLE
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.VERIFICATION_METHOD_INCOMPATIBLE in codes(result)


def test_invalid_public_key_length_is_distinct(sample_record, sample_proof, resolved_method):
    supplied = replace(resolved_method, public_key=b"short")
    result = verify_proof(sample_record, sample_proof, resolved_method=supplied)
    assert result.verification_method_compatibility == Status.INCOMPATIBLE
    assert ReasonCode.INVALID_PUBLIC_KEY_LENGTH in codes(result)


def test_invalid_signature_length_is_nonconforming(sample_record, sample_proof, resolved_method):
    malformed = replace(sample_proof, proofValue=b"short")
    result = verify_proof(sample_record, malformed, resolved_method=resolved_method)
    assert result.conformance == Status.NONCONFORMING
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.INVALID_PROOF_VALUE_LENGTH in codes(result)


def test_unsupported_version_is_not_signature_invalid(sample_record, sample_proof, resolved_method):
    future = replace(sample_proof, version=2)
    result = verify_proof(sample_record, future, resolved_method=resolved_method)
    assert result.version_support == Status.UNSUPPORTED
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.UNSUPPORTED_VERSION in codes(result)
    assert ReasonCode.SIGNATURE_INVALID not in codes(result)


def test_unsupported_cryptosuite_is_not_signature_invalid(sample_record, sample_proof, resolved_method):
    future = replace(sample_proof, cryptosuite="https://example.org/future-suite")
    result = verify_proof(sample_record, future, resolved_method=resolved_method)
    assert result.cryptosuite_support == Status.UNSUPPORTED
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.UNSUPPORTED_CRYPTOSUITE in codes(result)


def test_unsupported_commitment_algorithm_is_not_record_mismatch(sample_record, sample_proof, resolved_method):
    future = replace(sample_proof, recordCommitment=RecordCommitment(-999, b"\x00" * 32))
    result = verify_proof(sample_record, future, resolved_method=resolved_method)
    assert result.commitment_algorithm_support == Status.UNSUPPORTED
    assert result.record_binding == Status.NOT_EVALUATED
    assert ReasonCode.UNSUPPORTED_COMMITMENT_ALGORITHM in codes(result)
    assert ReasonCode.RECORD_COMMITMENT_MISMATCH not in codes(result)


def test_commitment_algorithm_policy_rejection_is_separate(sample_record, sample_proof, resolved_method):
    policy = VerificationPolicy(allowed_commitment_algorithms=frozenset())
    result = verify_proof(sample_record, sample_proof, resolved_method=resolved_method, policy=policy)
    assert result.commitment_algorithm_support == Status.REJECTED_BY_POLICY
    assert result.cryptographic_validity == Status.NOT_EVALUATED
    assert ReasonCode.COMMITMENT_ALGORITHM_REJECTED_BY_POLICY in codes(result)


def test_expected_purpose_mismatch_does_not_change_crypto_validity(sample_record, sample_proof, resolved_method):
    result = verify_proof(
        sample_record,
        sample_proof,
        resolved_method=resolved_method,
        expected_purpose="authorization",
    )
    assert result.cryptographic_validity == Status.VALID
    assert result.purpose_status == Status.MISMATCH
    assert ReasonCode.PURPOSE_MISMATCH in codes(result)


def test_expected_purpose_match(sample_record, sample_proof, resolved_method):
    result = verify_proof(
        sample_record,
        sample_proof,
        resolved_method=resolved_method,
        expected_purpose="assertion",
    )
    assert result.cryptographic_validity == Status.VALID
    assert result.purpose_status == Status.MATCH


def test_unknown_extension_purpose_can_still_be_cryptographically_verified(sample_record, test_seed, resolved_method):
    purpose = "https://example.org/purposes/custom"
    proof = create_proof(
        sample_record,
        proof_purpose=purpose,
        verification_method=TEST_METHOD,
        private_key=test_seed,
    )
    result = verify_proof(sample_record, proof, resolved_method=resolved_method)
    assert result.cryptographic_validity == Status.VALID
    assert result.purpose_status == Status.UNSUPPORTED
    assert ReasonCode.UNSUPPORTED_PROOF_PURPOSE in codes(result)


def test_domain_match_and_mismatch_are_context_results(sample_record, test_seed, resolved_method):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        domain="market.example",
    )
    match = verify_proof(sample_record, proof, resolved_method=resolved_method, expected_domain="market.example")
    mismatch = verify_proof(sample_record, proof, resolved_method=resolved_method, expected_domain="other.example")
    assert match.domain_status == Status.MATCH and match.cryptographic_validity == Status.VALID
    assert mismatch.domain_status == Status.MISMATCH and mismatch.cryptographic_validity == Status.VALID
    assert ReasonCode.DOMAIN_MISMATCH in codes(mismatch)


def test_required_domain_missing(sample_record, sample_proof, resolved_method):
    result = verify_proof(sample_record, sample_proof, resolved_method=resolved_method, expected_domain="market.example")
    assert result.domain_status == Status.MISMATCH
    assert ReasonCode.DOMAIN_REQUIRED in codes(result)


def test_challenge_match_and_mismatch_are_context_results(sample_record, test_seed, resolved_method):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        challenge=b"abc",
    )
    match = verify_proof(sample_record, proof, resolved_method=resolved_method, expected_challenge=b"abc")
    mismatch = verify_proof(sample_record, proof, resolved_method=resolved_method, expected_challenge=b"xyz")
    assert match.challenge_status == Status.MATCH
    assert mismatch.challenge_status == Status.MISMATCH
    assert mismatch.cryptographic_validity == Status.VALID
    assert ReasonCode.CHALLENGE_MISMATCH in codes(mismatch)


def test_required_challenge_missing(sample_record, sample_proof, resolved_method):
    result = verify_proof(sample_record, sample_proof, resolved_method=resolved_method, expected_challenge=b"abc")
    assert result.challenge_status == Status.MISMATCH
    assert ReasonCode.CHALLENGE_REQUIRED in codes(result)


def test_expiration_does_not_change_signature_validity(sample_record, test_seed, resolved_method):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        expires="2026-08-20T00:00:00Z",
    )
    result = verify_proof(
        sample_record,
        proof,
        resolved_method=resolved_method,
        evaluation_time=datetime(2026, 8, 21, tzinfo=timezone.utc),
    )
    assert result.cryptographic_validity == Status.VALID
    assert result.temporal_status == Status.EXPIRED
    assert ReasonCode.PROOF_EXPIRED in codes(result)


def test_nonexpired_proof_is_current(sample_record, test_seed, resolved_method):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        expires="2026-08-22T00:00:00Z",
    )
    result = verify_proof(
        sample_record,
        proof,
        resolved_method=resolved_method,
        evaluation_time=datetime(2026, 8, 21, tzinfo=timezone.utc),
    )
    assert result.temporal_status == Status.CURRENT


def test_created_timestamp_is_not_used_as_historical_proof(sample_record, test_seed, resolved_method):
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        created="2000-01-01T00:00:00Z",
    )
    result = verify_proof(sample_record, proof, resolved_method=resolved_method)
    assert result.cryptographic_validity == Status.VALID
    assert result.temporal_status == Status.NOT_EVALUATED


def test_unknown_noncritical_extension_is_warning_but_crypto_valid(sample_record, test_seed, resolved_method):
    ext = "https://example.org/ext/info"
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        extensions={ext: {"x": 1}},
    )
    result = verify_proof(sample_record, proof, resolved_method=resolved_method)
    assert result.cryptographic_validity == Status.VALID
    assert ReasonCode.UNKNOWN_NONCRITICAL_EXTENSION in warning_codes(result)


def test_unknown_critical_extension_is_unsupported_but_signature_can_still_be_checked(sample_record, test_seed, resolved_method):
    ext = "https://example.org/ext/security-condition"
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        extensions={ext: True},
        critical=(ext,),
    )
    result = verify_proof(sample_record, proof, resolved_method=resolved_method)
    assert result.critical_extension_status == Status.UNSUPPORTED
    assert result.cryptographic_validity == Status.VALID
    assert ReasonCode.UNSUPPORTED_CRITICAL_EXTENSION in codes(result)


def test_understood_critical_extension_passes(sample_record, test_seed, resolved_method):
    ext = "https://example.org/ext/security-condition"
    proof = create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
        extensions={ext: True},
        critical=(ext,),
    )
    policy = VerificationPolicy(understood_extensions=frozenset({ext}))
    result = verify_proof(sample_record, proof, resolved_method=resolved_method, policy=policy)
    assert result.critical_extension_status == Status.UNDERSTOOD
    assert result.cryptographic_validity == Status.VALID
    assert ReasonCode.UNSUPPORTED_CRITICAL_EXTENSION not in codes(result)


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (MethodStatus.RETIRED, ReasonCode.VERIFICATION_METHOD_RETIRED),
        (MethodStatus.EXPIRED, ReasonCode.VERIFICATION_METHOD_EXPIRED),
        (MethodStatus.SUSPENDED, ReasonCode.VERIFICATION_METHOD_SUSPENDED),
        (MethodStatus.REVOKED, ReasonCode.VERIFICATION_METHOD_REVOKED),
        (MethodStatus.COMPROMISED, ReasonCode.VERIFICATION_METHOD_COMPROMISED),
        (MethodStatus.UNKNOWN, ReasonCode.VERIFICATION_METHOD_STATUS_UNKNOWN),
    ],
)
def test_method_status_is_separate_from_crypto_validity(sample_record, sample_proof, resolved_method, status, code):
    result = verify_proof(
        sample_record,
        sample_proof,
        resolved_method=resolved_method,
        verification_method_status=status,
    )
    assert result.cryptographic_validity == Status.VALID
    assert result.verification_method_status == status
    assert code in warning_codes(result)


def test_resolution_provenance_is_exposed(sample_record, sample_proof, resolved_method):
    result = verify_proof(sample_record, sample_proof, resolved_method=resolved_method)
    assert result.resolution_provenance == resolved_method.provenance


def test_no_hidden_network_resolution_occurs(sample_record, sample_proof):
    # The API requires explicit material; a missing method is an UNAVAILABLE result.
    result = verify_proof(sample_record, sample_proof, resolved_method=None)
    assert result.verification_method_resolution == Status.UNAVAILABLE

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("created", "2026-08-20T00:00:00Z"),
        ("expires", "2027-08-20T00:00:00Z"),
        ("domain", "market.example"),
        ("challenge", b"challenge"),
        ("nonce", b"nonce"),
    ],
)
def test_adding_authenticated_metadata_without_resigning_invalidates_signature(
    sample_record, sample_proof, resolved_method, field, value
):
    mutated = replace(sample_proof, **{field: value})
    result = verify_proof(sample_record, mutated, resolved_method=resolved_method)
    assert result.record_binding == Status.VALID
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)


def test_mutating_authenticated_extension_without_resigning_invalidates_signature(
    sample_record, sample_proof, resolved_method
):
    mutated = replace(sample_proof, extensions={"https://example.org/ext/info": True})
    result = verify_proof(sample_record, mutated, resolved_method=resolved_method)
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)


def test_mutating_critical_declaration_without_resigning_invalidates_signature(
    sample_record, sample_proof, resolved_method
):
    ext = "https://example.org/ext/security-condition"
    mutated = replace(sample_proof, extensions={ext: True}, critical=(ext,))
    policy = VerificationPolicy(understood_extensions=frozenset({ext}))
    result = verify_proof(sample_record, mutated, resolved_method=resolved_method, policy=policy)
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)


def test_mutating_proof_value_is_signature_invalid(sample_record, sample_proof, resolved_method):
    tampered = bytearray(sample_proof.proofValue)
    tampered[-1] ^= 1
    mutated = replace(sample_proof, proofValue=bytes(tampered))
    result = verify_proof(sample_record, mutated, resolved_method=resolved_method)
    assert result.cryptographic_validity == Status.INVALID
    assert ReasonCode.SIGNATURE_INVALID in codes(result)
