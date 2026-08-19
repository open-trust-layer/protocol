"""Algorithm-agile record commitments for Specification 0004."""

from __future__ import annotations

import hashlib

from ..constants import SHA256_COSE_ALGORITHM_ID
from ..errors import UnsupportedFeatureError
from ..model.proof import RecordCommitment
from ..model.record import RecordV1
from ..encoding.record_identity import record_identity_bytes

_SUPPORTED = frozenset({SHA256_COSE_ALGORITHM_ID})


def supported_commitment_algorithms() -> frozenset[int]:
    return _SUPPORTED


def digest_bytes(data: bytes, algorithm: int) -> bytes:
    if algorithm == SHA256_COSE_ALGORITHM_ID:
        return hashlib.sha256(data).digest()
    raise UnsupportedFeatureError(
        f"unsupported record commitment algorithm: {algorithm}",
        code="UNSUPPORTED_COMMITMENT_ALGORITHM",
    )


def record_commitment(record: RecordV1, algorithm: int = SHA256_COSE_ALGORITHM_ID) -> RecordCommitment:
    return RecordCommitment(algorithm=algorithm, digest=digest_bytes(record_identity_bytes(record), algorithm))
