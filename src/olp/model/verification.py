"""Structured Specification 0004 verification results and supplied key model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from ..constants import CORE_PROOF_PURPOSES, MANDATORY_CRYPTOSUITE, SHA256_COSE_ALGORITHM_ID


class Status(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    CONFORMING = "CONFORMING"
    NONCONFORMING = "NONCONFORMING"
    VALID = "VALID"
    INVALID = "INVALID"
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    RESOLVED = "RESOLVED"
    UNAVAILABLE = "UNAVAILABLE"
    COMPATIBLE = "COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNDERSTOOD = "UNDERSTOOD"
    UNKNOWN = "UNKNOWN"
    CURRENT = "CURRENT"
    EXPIRED = "EXPIRED"
    REJECTED_BY_POLICY = "REJECTED_BY_POLICY"


class ResolutionProvenance(StrEnum):
    SUPPLIED = "supplied"
    LOCAL_STORE = "local_store"
    RESOLVER = "resolver"
    HISTORICAL_EVIDENCE = "historical_evidence"


class MethodStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    COMPROMISED = "COMPROMISED"
    UNKNOWN = "UNKNOWN"


class ReasonCode(StrEnum):
    MALFORMED_PROOF = "MALFORMED_PROOF"
    DUPLICATE_PROPERTY = "DUPLICATE_PROPERTY"
    INVALID_CORE_PROPERTY = "INVALID_CORE_PROPERTY"
    INVALID_EXTENSION_NAME = "INVALID_EXTENSION_NAME"
    INVALID_EXTENSION_VALUE = "INVALID_EXTENSION_VALUE"
    INVALID_CRITICAL_DECLARATION = "INVALID_CRITICAL_DECLARATION"
    UNSUPPORTED_VERSION = "UNSUPPORTED_VERSION"
    UNSUPPORTED_CRYPTOSUITE = "UNSUPPORTED_CRYPTOSUITE"
    UNSUPPORTED_COMMITMENT_ALGORITHM = "UNSUPPORTED_COMMITMENT_ALGORITHM"
    COMMITMENT_ALGORITHM_REJECTED_BY_POLICY = "COMMITMENT_ALGORITHM_REJECTED_BY_POLICY"
    RECORD_COMMITMENT_MISMATCH = "RECORD_COMMITMENT_MISMATCH"
    UNSUPPORTED_CRITICAL_EXTENSION = "UNSUPPORTED_CRITICAL_EXTENSION"
    UNKNOWN_NONCRITICAL_EXTENSION = "UNKNOWN_NONCRITICAL_EXTENSION"
    UNSUPPORTED_VERIFICATION_METHOD = "UNSUPPORTED_VERIFICATION_METHOD"
    VERIFICATION_METHOD_UNAVAILABLE = "VERIFICATION_METHOD_UNAVAILABLE"
    VERIFICATION_METHOD_MISMATCH = "VERIFICATION_METHOD_MISMATCH"
    VERIFICATION_METHOD_INCOMPATIBLE = "VERIFICATION_METHOD_INCOMPATIBLE"
    VERIFICATION_METHOD_MALFORMED = "VERIFICATION_METHOD_MALFORMED"
    INVALID_PROOF_VALUE_LENGTH = "INVALID_PROOF_VALUE_LENGTH"
    INVALID_PUBLIC_KEY_LENGTH = "INVALID_PUBLIC_KEY_LENGTH"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    UNSUPPORTED_PROOF_PURPOSE = "UNSUPPORTED_PROOF_PURPOSE"
    PURPOSE_MISMATCH = "PURPOSE_MISMATCH"
    DOMAIN_REQUIRED = "DOMAIN_REQUIRED"
    DOMAIN_MISMATCH = "DOMAIN_MISMATCH"
    CHALLENGE_REQUIRED = "CHALLENGE_REQUIRED"
    CHALLENGE_MISMATCH = "CHALLENGE_MISMATCH"
    PROOF_EXPIRED = "PROOF_EXPIRED"
    VERIFICATION_METHOD_RETIRED = "VERIFICATION_METHOD_RETIRED"
    VERIFICATION_METHOD_EXPIRED = "VERIFICATION_METHOD_EXPIRED"
    VERIFICATION_METHOD_SUSPENDED = "VERIFICATION_METHOD_SUSPENDED"
    VERIFICATION_METHOD_REVOKED = "VERIFICATION_METHOD_REVOKED"
    VERIFICATION_METHOD_COMPROMISED = "VERIFICATION_METHOD_COMPROMISED"
    VERIFICATION_METHOD_STATUS_UNKNOWN = "VERIFICATION_METHOD_STATUS_UNKNOWN"


@dataclass(frozen=True, slots=True)
class VerificationIssue:
    code: ReasonCode
    message: str


@dataclass(frozen=True, slots=True)
class ResolvedVerificationMethod:
    identifier: str
    key_type: str
    public_key: bytes
    provenance: ResolutionProvenance = ResolutionProvenance.SUPPLIED


@dataclass(frozen=True, slots=True)
class VerificationPolicy:
    understood_extensions: frozenset[str] = frozenset()
    understood_proof_purposes: frozenset[str] = CORE_PROOF_PURPOSES
    allowed_commitment_algorithms: frozenset[int] | None = frozenset({SHA256_COSE_ALGORITHM_ID})
    allowed_cryptosuites: frozenset[str] | None = frozenset({MANDATORY_CRYPTOSUITE})


@dataclass(frozen=True, slots=True)
class VerificationResult:
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
    resolution_provenance: ResolutionProvenance | None = None
    warnings: tuple[VerificationIssue, ...] = field(default_factory=tuple)
    errors: tuple[VerificationIssue, ...] = field(default_factory=tuple)

    @property
    def cryptographically_valid(self) -> bool:
        return self.cryptographic_validity == Status.VALID

    @property
    def fully_processed(self) -> bool:
        """Convenience only: no unsupported/unavailable/nonconforming dimensions or errors."""
        blocked = {
            Status.NONCONFORMING,
            Status.UNSUPPORTED,
            Status.UNAVAILABLE,
            Status.INCOMPATIBLE,
            Status.REJECTED_BY_POLICY,
        }
        dimensions = (
            self.conformance,
            self.version_support,
            self.cryptosuite_support,
            self.commitment_algorithm_support,
            self.critical_extension_status,
            self.verification_method_resolution,
            self.verification_method_compatibility,
        )
        return not self.errors and not any(value in blocked for value in dimensions)
