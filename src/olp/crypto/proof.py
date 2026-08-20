"""High-level OLP v1 proof creation and structured verification."""

from __future__ import annotations

import hmac
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ..constants import (
    MANDATORY_CRYPTOSUITE,
    PROOF_TYPE,
    PROOF_VERSION,
    SHA256_COSE_ALGORITHM_ID,
)
from ..encoding.deterministic_cbor import encode
from ..encoding.proof_input import build_proof_input, proof_input_from_proof
from ..encoding.record_identity import record_identity_bytes
from ..errors import ConformanceError, KeyMaterialError, UnsupportedFeatureError
from ..model.proof import OLPProof, RecordCommitment, parse_rfc3339
from ..model.record import RecordV1
from ..model.verification import (
    MethodStatus,
    ReasonCode,
    ResolvedVerificationMethod,
    Status,
    VerificationIssue,
    VerificationPolicy,
    VerificationResult,
)
from .commitments import digest_bytes, record_commitment, supported_commitment_algorithms
from .ed25519 import SIGNATURE_LENGTH, sign as ed25519_sign, verify as ed25519_verify


@dataclass(slots=True)
class _ResultBuilder:
    conformance: Status = Status.NOT_EVALUATED
    record_binding: Status = Status.NOT_EVALUATED
    version_support: Status = Status.NOT_EVALUATED
    cryptosuite_support: Status = Status.NOT_EVALUATED
    commitment_algorithm_support: Status = Status.NOT_EVALUATED
    critical_extension_status: Status = Status.NOT_EVALUATED
    verification_method_resolution: Status = Status.NOT_EVALUATED
    verification_method_compatibility: Status = Status.NOT_EVALUATED
    cryptographic_validity: Status = Status.NOT_EVALUATED
    purpose_status: Status = Status.NOT_EVALUATED
    domain_status: Status = Status.NOT_EVALUATED
    challenge_status: Status = Status.NOT_EVALUATED
    temporal_status: Status = Status.NOT_EVALUATED
    verification_method_status: MethodStatus | Status = Status.NOT_EVALUATED
    resolution_provenance: Any = None
    warnings: list[VerificationIssue] = None  # type: ignore[assignment]
    errors: list[VerificationIssue] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.warnings = []
        self.errors = []

    def error(self, code: ReasonCode, message: str) -> None:
        self.errors.append(VerificationIssue(code, message))

    def warning(self, code: ReasonCode, message: str) -> None:
        self.warnings.append(VerificationIssue(code, message))

    def finish(self) -> VerificationResult:
        return VerificationResult(
            conformance=self.conformance,
            record_binding=self.record_binding,
            version_support=self.version_support,
            cryptosuite_support=self.cryptosuite_support,
            commitment_algorithm_support=self.commitment_algorithm_support,
            critical_extension_status=self.critical_extension_status,
            verification_method_resolution=self.verification_method_resolution,
            verification_method_compatibility=self.verification_method_compatibility,
            cryptographic_validity=self.cryptographic_validity,
            purpose_status=self.purpose_status,
            domain_status=self.domain_status,
            challenge_status=self.challenge_status,
            temporal_status=self.temporal_status,
            verification_method_status=self.verification_method_status,
            resolution_provenance=self.resolution_provenance,
            warnings=tuple(self.warnings),
            errors=tuple(self.errors),
        )


def create_proof(
    record: RecordV1,
    *,
    proof_purpose: str,
    verification_method: str,
    private_key: bytes | Ed25519PrivateKey,
    cryptosuite: str = MANDATORY_CRYPTOSUITE,
    commitment_algorithm: int = SHA256_COSE_ALGORITHM_ID,
    created: str | None = None,
    expires: str | None = None,
    domain: str | None = None,
    challenge: bytes | None = None,
    nonce: bytes | None = None,
    extensions: dict[str, Any] | None = None,
    critical: tuple[str, ...] | list[str] = (),
) -> OLPProof:
    """Create an immutable OLP v1 proof using the mandatory reference suite."""

    record.validate()
    if cryptosuite != MANDATORY_CRYPTOSUITE:
        raise UnsupportedFeatureError(
            f"proof producer does not implement cryptosuite {cryptosuite!r}",
            code="UNSUPPORTED_CRYPTOSUITE",
        )
    if commitment_algorithm not in supported_commitment_algorithms():
        raise UnsupportedFeatureError(
            f"proof producer does not implement commitment algorithm {commitment_algorithm}",
            code="UNSUPPORTED_COMMITMENT_ALGORITHM",
        )

    commitment = record_commitment(record, commitment_algorithm)
    # A zero signature is used only to run all proof-object validation before
    # signing. It never leaves this function.
    prototype = OLPProof(
        type=PROOF_TYPE,
        version=PROOF_VERSION,
        cryptosuite=cryptosuite,
        proofPurpose=proof_purpose,
        verificationMethod=verification_method,
        recordCommitment=commitment,
        proofValue=b"\x00" * SIGNATURE_LENGTH,
        created=created,
        expires=expires,
        domain=domain,
        challenge=challenge,
        nonce=nonce,
        critical=tuple(critical),
        extensions=extensions or {},
    )
    prototype.validate_structure()
    message = encode(proof_input_from_proof(prototype))
    signature = ed25519_sign(private_key, message)
    proof = replace(prototype, proofValue=signature)
    proof.validate_structure()
    return proof


def verify_proof(
    record: RecordV1,
    proof: OLPProof,
    *,
    resolved_method: ResolvedVerificationMethod | None,
    expected_purpose: str | None = None,
    expected_domain: str | None = None,
    expected_challenge: bytes | None = None,
    evaluation_time: datetime | None = None,
    verification_method_status: MethodStatus | None = None,
    policy: VerificationPolicy | None = None,
) -> VerificationResult:
    """Verify a proof while preserving the Specification 0004 stage distinctions.

    The function performs no implicit resolution and no network I/O. Verification
    material must be supplied explicitly through ``resolved_method``.
    """

    policy = policy or VerificationPolicy()
    result = _ResultBuilder()

    try:
        proof.validate_structure()
    except ConformanceError as exc:
        result.conformance = Status.NONCONFORMING
        code = _reason_from_code(exc.code, fallback=ReasonCode.MALFORMED_PROOF)
        result.error(code, str(exc))
        return result.finish()

    result.conformance = Status.CONFORMING

    if proof.version != PROOF_VERSION:
        result.version_support = Status.UNSUPPORTED
        result.error(ReasonCode.UNSUPPORTED_VERSION, f"unsupported proof version {proof.version}")
        return result.finish()
    result.version_support = Status.SUPPORTED

    suite_supported = proof.cryptosuite == MANDATORY_CRYPTOSUITE
    if not suite_supported:
        result.cryptosuite_support = Status.UNSUPPORTED
        result.error(ReasonCode.UNSUPPORTED_CRYPTOSUITE, f"unsupported cryptosuite {proof.cryptosuite!r}")
    elif policy.allowed_cryptosuites is not None and proof.cryptosuite not in policy.allowed_cryptosuites:
        result.cryptosuite_support = Status.REJECTED_BY_POLICY
        result.error(
            ReasonCode.CRYPTOSUITE_REJECTED_BY_POLICY,
            f"cryptosuite {proof.cryptosuite!r} rejected by local policy",
        )
    else:
        result.cryptosuite_support = Status.SUPPORTED

    unknown_critical = [item for item in proof.critical if item not in policy.understood_extensions]
    unknown_noncritical = [
        key for key in proof.extensions if key not in policy.understood_extensions and key not in proof.critical
    ]
    if unknown_critical:
        result.critical_extension_status = Status.UNSUPPORTED
        result.error(
            ReasonCode.UNSUPPORTED_CRITICAL_EXTENSION,
            "unsupported critical extension(s): " + ", ".join(sorted(unknown_critical)),
        )
    else:
        result.critical_extension_status = Status.UNDERSTOOD
    for extension in sorted(unknown_noncritical):
        result.warning(
            ReasonCode.UNKNOWN_NONCRITICAL_EXTENSION,
            f"unknown non-critical extension authenticated but not interpreted: {extension}",
        )

    algorithm = proof.recordCommitment.algorithm
    if algorithm not in supported_commitment_algorithms():
        result.commitment_algorithm_support = Status.UNSUPPORTED
        result.error(
            ReasonCode.UNSUPPORTED_COMMITMENT_ALGORITHM,
            f"unsupported commitment algorithm {algorithm}",
        )
    else:
        result.commitment_algorithm_support = Status.SUPPORTED
        if policy.allowed_commitment_algorithms is not None and algorithm not in policy.allowed_commitment_algorithms:
            result.commitment_algorithm_support = Status.REJECTED_BY_POLICY
            result.error(
                ReasonCode.COMMITMENT_ALGORITHM_REJECTED_BY_POLICY,
                f"commitment algorithm {algorithm} rejected by local policy",
            )
        # Mathematical record binding remains evaluable even when local policy
        # rejects a technically supported algorithm. Policy is a separate
        # dimension and MUST NOT rewrite cryptographic history.
        canonical_record = record_identity_bytes(record)
        actual_digest = digest_bytes(canonical_record, algorithm)
        if hmac.compare_digest(actual_digest, proof.recordCommitment.digest):
            result.record_binding = Status.VALID
        else:
            result.record_binding = Status.INVALID
            result.error(ReasonCode.RECORD_COMMITMENT_MISMATCH, "record commitment does not match supplied record")

    if resolved_method is None:
        result.verification_method_resolution = Status.UNAVAILABLE
        result.error(ReasonCode.VERIFICATION_METHOD_UNAVAILABLE, "verification method material was not supplied")
    else:
        result.verification_method_resolution = Status.RESOLVED
        result.resolution_provenance = resolved_method.provenance
        if resolved_method.identifier != proof.verificationMethod:
            result.verification_method_compatibility = Status.MISMATCH
            result.error(
                ReasonCode.VERIFICATION_METHOD_MISMATCH,
                "resolved verification method id does not match authenticated verificationMethod",
            )
        elif suite_supported and resolved_method.key_type != "Ed25519":
            result.verification_method_compatibility = Status.INCOMPATIBLE
            result.error(
                ReasonCode.VERIFICATION_METHOD_INCOMPATIBLE,
                f"{proof.cryptosuite} requires Ed25519 key material, got {resolved_method.key_type!r}",
            )
        elif suite_supported and (not isinstance(resolved_method.public_key, bytes) or len(resolved_method.public_key) != 32):
            result.verification_method_compatibility = Status.INCOMPATIBLE
            result.error(ReasonCode.INVALID_PUBLIC_KEY_LENGTH, "Ed25519 public key MUST contain exactly 32 octets")
        else:
            result.verification_method_compatibility = Status.COMPATIBLE

    prerequisites = (
        suite_supported
        and algorithm in supported_commitment_algorithms()
        and result.record_binding == Status.VALID
        and resolved_method is not None
        and result.verification_method_compatibility == Status.COMPATIBLE
    )
    if prerequisites:
        try:
            message = encode(proof_input_from_proof(proof))
            valid = ed25519_verify(resolved_method.public_key, proof.proofValue, message)
        except KeyMaterialError as exc:
            result.cryptographic_validity = Status.NOT_EVALUATED
            result.error(ReasonCode.VERIFICATION_METHOD_MALFORMED, str(exc))
        else:
            result.cryptographic_validity = Status.VALID if valid else Status.INVALID
            if not valid:
                result.error(ReasonCode.SIGNATURE_INVALID, "Ed25519 signature verification failed")

    _evaluate_purpose(result, proof, expected_purpose, policy)
    _evaluate_domain(result, proof, expected_domain)
    _evaluate_challenge(result, proof, expected_challenge)
    _evaluate_time(result, proof, evaluation_time)
    _evaluate_method_status(result, verification_method_status)

    return result.finish()


def _evaluate_purpose(
    result: _ResultBuilder,
    proof: OLPProof,
    expected_purpose: str | None,
    policy: VerificationPolicy,
) -> None:
    understood = proof.proofPurpose in policy.understood_proof_purposes
    if not understood:
        result.purpose_status = Status.UNSUPPORTED
        result.error(ReasonCode.UNSUPPORTED_PROOF_PURPOSE, f"unsupported proof purpose {proof.proofPurpose!r}")
        return
    if expected_purpose is None:
        result.purpose_status = Status.UNDERSTOOD
    elif proof.proofPurpose == expected_purpose:
        result.purpose_status = Status.MATCH
    else:
        result.purpose_status = Status.MISMATCH
        result.error(
            ReasonCode.PURPOSE_MISMATCH,
            f"proof purpose {proof.proofPurpose!r} does not match expected {expected_purpose!r}",
        )


def _evaluate_domain(result: _ResultBuilder, proof: OLPProof, expected_domain: str | None) -> None:
    if expected_domain is None:
        return
    if proof.domain is None:
        result.domain_status = Status.MISMATCH
        result.error(ReasonCode.DOMAIN_REQUIRED, "caller required a domain but proof has none")
    elif proof.domain == expected_domain:
        result.domain_status = Status.MATCH
    else:
        result.domain_status = Status.MISMATCH
        result.error(ReasonCode.DOMAIN_MISMATCH, "authenticated domain does not match caller expectation")


def _evaluate_challenge(result: _ResultBuilder, proof: OLPProof, expected_challenge: bytes | None) -> None:
    if expected_challenge is None:
        return
    if proof.challenge is None:
        result.challenge_status = Status.MISMATCH
        result.error(ReasonCode.CHALLENGE_REQUIRED, "caller required a challenge but proof has none")
    elif hmac.compare_digest(proof.challenge, expected_challenge):
        result.challenge_status = Status.MATCH
    else:
        result.challenge_status = Status.MISMATCH
        result.error(ReasonCode.CHALLENGE_MISMATCH, "authenticated challenge does not match caller expectation")


def _evaluate_time(result: _ResultBuilder, proof: OLPProof, evaluation_time: datetime | None) -> None:
    if evaluation_time is None:
        return
    if evaluation_time.tzinfo is None:
        raise ValueError("evaluation_time must be timezone-aware")
    if proof.expires is None:
        result.temporal_status = Status.CURRENT
        return
    if evaluation_time > parse_rfc3339(proof.expires):
        result.temporal_status = Status.EXPIRED
        result.error(ReasonCode.PROOF_EXPIRED, "proof is expired at the supplied evaluation time")
    else:
        result.temporal_status = Status.CURRENT


def _evaluate_method_status(result: _ResultBuilder, status: MethodStatus | None) -> None:
    if status is None:
        return
    result.verification_method_status = status
    code_by_status = {
        MethodStatus.RETIRED: ReasonCode.VERIFICATION_METHOD_RETIRED,
        MethodStatus.EXPIRED: ReasonCode.VERIFICATION_METHOD_EXPIRED,
        MethodStatus.SUSPENDED: ReasonCode.VERIFICATION_METHOD_SUSPENDED,
        MethodStatus.REVOKED: ReasonCode.VERIFICATION_METHOD_REVOKED,
        MethodStatus.COMPROMISED: ReasonCode.VERIFICATION_METHOD_COMPROMISED,
        MethodStatus.UNKNOWN: ReasonCode.VERIFICATION_METHOD_STATUS_UNKNOWN,
    }
    code = code_by_status.get(status)
    if code is not None:
        result.warning(code, f"verification method status: {status.value}")


def _reason_from_code(code: str, *, fallback: ReasonCode) -> ReasonCode:
    try:
        return ReasonCode(code)
    except ValueError:
        return fallback
