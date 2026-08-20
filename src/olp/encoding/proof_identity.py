"""Specification 0005 Proof Identity (OLP-PIE-1)."""

from __future__ import annotations

import hashlib

from ..model.proof import OLPProof
from .deterministic_cbor import CborLimits, DEFAULT_LIMITS, encode
from .proof_input import proof_input_bytes


def proof_identity_preimage(proof: OLPProof, *, limits: CborLimits = DEFAULT_LIMITS) -> tuple[object, ...]:
    """Return the exact four-element ProofIdentityPreimageV1 value."""
    return ("OLP-PROOF-ID", 1, proof_input_bytes(proof, limits=limits), proof.proofValue)


def proof_identity_bytes(proof: OLPProof, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    """Return exact OLP-PIE-1 bytes for a conforming v1 proof."""
    return encode(proof_identity_preimage(proof, limits=limits), limits=limits)


def proof_identity(proof: OLPProof, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    """Return the stable 32-octet Specification 0005 Proof Identity digest."""
    return hashlib.sha256(proof_identity_bytes(proof, limits=limits)).digest()
