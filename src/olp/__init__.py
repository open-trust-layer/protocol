"""Open Layer Protocol Draft v0.1 reference implementation core.

Milestone 13 implements the deterministic record/proof vertical slice from
Specifications 0003 and 0004. The package intentionally performs no implicit
network resolution.
"""

from .constants import MANDATORY_CRYPTOSUITE, SHA256_COSE_ALGORITHM_ID
from .crypto.proof import create_proof, verify_proof
from .encoding.record_identity import record_identity, record_identity_bytes, record_identity_text
from .model.proof import OLPProof, RecordCommitment
from .model.record import RecordV1
from .model.verification import ResolvedVerificationMethod, VerificationPolicy, VerificationResult

__all__ = [
    "MANDATORY_CRYPTOSUITE",
    "SHA256_COSE_ALGORITHM_ID",
    "OLPProof",
    "RecordCommitment",
    "RecordV1",
    "ResolvedVerificationMethod",
    "VerificationPolicy",
    "VerificationResult",
    "create_proof",
    "verify_proof",
    "record_identity",
    "record_identity_bytes",
    "record_identity_text",
]
