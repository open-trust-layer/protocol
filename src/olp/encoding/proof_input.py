"""Construction of the exact nine-element OLP ProofInputV1 structure."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from ..constants import METADATA_LABELS, PROOF_DOMAIN, PROOF_INPUT_VERSION
from ..errors import ConformanceError
from ..model.proof import OLPProof, RecordCommitment
from ..values import validate_proof_value
from .deterministic_cbor import CborLimits, DEFAULT_LIMITS, encode


def metadata_map(
    *,
    created: str | None = None,
    expires: str | None = None,
    domain: str | None = None,
    challenge: bytes | None = None,
    nonce: bytes | None = None,
) -> Mapping[int, Any]:
    result: dict[int, Any] = {}
    if created is not None:
        result[METADATA_LABELS["created"]] = created
    if expires is not None:
        result[METADATA_LABELS["expires"]] = expires
    if domain is not None:
        result[METADATA_LABELS["domain"]] = domain
    if challenge is not None:
        result[METADATA_LABELS["challenge"]] = challenge
    if nonce is not None:
        result[METADATA_LABELS["nonce"]] = nonce
    return MappingProxyType(result)


def build_proof_input(
    *,
    cryptosuite: str,
    proof_purpose: str,
    verification_method: str,
    record_commitment: RecordCommitment,
    created: str | None = None,
    expires: str | None = None,
    domain: str | None = None,
    challenge: bytes | None = None,
    nonce: bytes | None = None,
    extensions: Mapping[str, Any] | None = None,
    critical: tuple[str, ...] | list[str] = (),
) -> tuple[Any, ...]:
    ext = dict(extensions or {})
    # ProofInputV1 fields inherit the structural constraints of the proof
    # properties they authenticate. Validate them here as well so callers of
    # the direct ProofInput builder cannot bypass URI, timestamp, extension,
    # or critical-declaration checks that OLPProof.validate_structure enforces.
    probe = OLPProof(
        type="OLPProof",
        version=1,
        cryptosuite=cryptosuite,
        proofPurpose=proof_purpose,
        verificationMethod=verification_method,
        recordCommitment=record_commitment,
        proofValue=b"\x00" * 64,
        created=created,
        expires=expires,
        domain=domain,
        challenge=challenge,
        nonce=nonce,
        critical=tuple(critical),
        extensions=ext,
    )
    probe.validate_structure()
    sorted_critical = probe.sorted_critical()
    metadata = metadata_map(
        created=created,
        expires=expires,
        domain=domain,
        challenge=challenge,
        nonce=nonce,
    )
    value = (
        PROOF_DOMAIN,
        PROOF_INPUT_VERSION,
        cryptosuite,
        proof_purpose,
        verification_method,
        record_commitment.proof_input_value(),
        metadata,
        ext,
        sorted_critical,
    )
    validate_proof_value(value, path="ProofInputV1")
    if len(value) != 9:
        raise ConformanceError("ProofInputV1 MUST contain exactly nine elements")
    return value


def proof_input_from_proof(proof: OLPProof) -> tuple[Any, ...]:
    proof.validate_structure()
    return build_proof_input(
        cryptosuite=proof.cryptosuite,
        proof_purpose=proof.proofPurpose,
        verification_method=proof.verificationMethod,
        record_commitment=proof.recordCommitment,
        created=proof.created,
        expires=proof.expires,
        domain=proof.domain,
        challenge=proof.challenge,
        nonce=proof.nonce,
        extensions=proof.extensions,
        critical=proof.critical,
    )


def proof_input_bytes(proof: OLPProof, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    return encode(proof_input_from_proof(proof), limits=limits)


def encode_proof_input(value: tuple[Any, ...], *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    validate_proof_value(value, path="ProofInputV1")
    if len(value) != 9:
        raise ConformanceError("ProofInputV1 MUST contain exactly nine elements")
    return encode(value, limits=limits)
