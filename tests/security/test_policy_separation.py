from olp.crypto.proof import verify_proof
from olp.model.verification import ReasonCode, Status, VerificationPolicy


def _codes(result):
    return {issue.code for issue in result.errors}


def test_supported_cryptosuite_can_be_policy_rejected_without_erasing_signature_math(sample_record, sample_proof, resolved_method):
    result = verify_proof(
        sample_record,
        sample_proof,
        resolved_method=resolved_method,
        policy=VerificationPolicy(allowed_cryptosuites=frozenset()),
    )
    assert result.cryptosuite_support == Status.REJECTED_BY_POLICY
    assert result.record_binding == Status.VALID
    assert result.cryptographic_validity == Status.VALID
    assert ReasonCode.CRYPTOSUITE_REJECTED_BY_POLICY in _codes(result)


def test_supported_commitment_can_be_policy_rejected_without_erasing_signature_math(sample_record, sample_proof, resolved_method):
    result = verify_proof(
        sample_record,
        sample_proof,
        resolved_method=resolved_method,
        policy=VerificationPolicy(allowed_commitment_algorithms=frozenset()),
    )
    assert result.commitment_algorithm_support == Status.REJECTED_BY_POLICY
    assert result.record_binding == Status.VALID
    assert result.cryptographic_validity == Status.VALID
    assert ReasonCode.COMMITMENT_ALGORITHM_REJECTED_BY_POLICY in _codes(result)
