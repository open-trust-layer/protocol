import pytest

from olp.encoding.record_identity import record_identity_bytes
from olp.errors import ConformanceError
from olp.model.record import RecordV1
from olp.model.proof import RecordCommitment
from olp.encoding.proof_input import build_proof_input


def test_boolean_record_version_is_not_integer_one():
    with pytest.raises(ConformanceError):
        record_identity_bytes(RecordV1(True, 'claim', {}))


def test_direct_proof_input_builder_rejects_relative_verification_method():
    with pytest.raises(ConformanceError):
        build_proof_input(
            cryptosuite='eddsa-ed25519-v1',
            proof_purpose='assertion',
            verification_method='relative-key',
            record_commitment=RecordCommitment(-16, b'\x00' * 32),
        )
