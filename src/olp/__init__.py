"""Open Layer Protocol Draft v0.1 reference implementation core.

The package implements the deterministic record/proof core from Specifications
0003 and 0004 plus the Milestone 16 Evidence Graph Core from Specification 0005 and Milestone 17 adversarial hardening. The package intentionally performs no implicit network resolution.
"""

from .constants import MANDATORY_CRYPTOSUITE, SHA256_COSE_ALGORITHM_ID
from .crypto.proof import create_proof, verify_proof
from .encoding.record_identity import record_identity, record_identity_bytes, record_identity_text
from .encoding.proof_identity import proof_identity, proof_identity_bytes, proof_identity_preimage
from .evidence import EvidenceGraph, parse_relationship_record, proof_ref, record_ref, relationship_record, verify_evidence_ref
from .model.evidence import EvidenceKind, EvidenceRefV1, RelationshipStatementV1
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
    "proof_identity",
    "proof_identity_bytes",
    "proof_identity_preimage",
    "EvidenceKind",
    "EvidenceRefV1",
    "RelationshipStatementV1",
    "EvidenceGraph",
    "record_ref",
    "proof_ref",
    "verify_evidence_ref",
    "relationship_record",
    "parse_relationship_record",
]
