from __future__ import annotations

import pytest

from olp.constants import SHA256_COSE_ALGORITHM_ID
from olp.crypto.commitments import digest_bytes, record_commitment, supported_commitment_algorithms
from olp.encoding.record_identity import record_identity
from olp.errors import UnsupportedFeatureError


def test_sha256_is_mandatory_supported_algorithm():
    assert SHA256_COSE_ALGORITHM_ID in supported_commitment_algorithms()


def test_sha256_record_commitment_matches_record_identity_digest(sample_record):
    commitment = record_commitment(sample_record)
    assert commitment.algorithm == -16
    assert commitment.digest == record_identity(sample_record)


def test_hash_algorithm_is_not_inferred_from_digest_length():
    with pytest.raises(UnsupportedFeatureError) as exc:
        digest_bytes(b"data", -999)
    assert exc.value.code == "UNSUPPORTED_COMMITMENT_ALGORITHM"
