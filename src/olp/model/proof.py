"""Specification 0004 proof abstract data model."""

from __future__ import annotations

import calendar
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from ..constants import CORE_PROOF_PROPERTIES, CORE_PROOF_PURPOSES, MANDATORY_CRYPTOSUITE, PROOF_TYPE
from ..errors import ConformanceError
from ..values import freeze_value, is_absolute_uri, is_semantic_identifier, validate_proof_value

_RFC3339_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"[Tt](?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?P<fraction>\.\d+)?"
    r"(?P<zone>[Zz]|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True, slots=True)
class RecordCommitment:
    algorithm: int
    digest: bytes

    def __post_init__(self) -> None:
        if isinstance(self.algorithm, bool) or not isinstance(self.algorithm, int):
            raise ConformanceError("record commitment algorithm MUST be an integer")
        if not isinstance(self.digest, bytes) or not self.digest:
            raise ConformanceError("record commitment digest MUST be a non-empty byte string")

    def proof_input_value(self) -> tuple[int, bytes]:
        return (self.algorithm, self.digest)


@dataclass(frozen=True, slots=True)
class OLPProof:
    type: str
    version: int
    cryptosuite: str
    proofPurpose: str
    verificationMethod: str
    recordCommitment: RecordCommitment
    proofValue: bytes
    created: str | None = None
    expires: str | None = None
    domain: str | None = None
    challenge: bytes | None = None
    nonce: bytes | None = None
    critical: tuple[str, ...] = ()
    extensions: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "proofValue", bytes(self.proofValue) if isinstance(self.proofValue, bytearray) else self.proofValue)
        object.__setattr__(self, "challenge", bytes(self.challenge) if isinstance(self.challenge, bytearray) else self.challenge)
        object.__setattr__(self, "nonce", bytes(self.nonce) if isinstance(self.nonce, bytearray) else self.nonce)
        object.__setattr__(self, "critical", tuple(self.critical))
        if isinstance(self.extensions, Mapping):
            object.__setattr__(
                self,
                "extensions",
                MappingProxyType({key: freeze_value(value) for key, value in self.extensions.items()}),
            )

    def validate_structure(self) -> None:
        """Validate v1-independent shape plus v1 field constraints where semantics are known."""
        if self.type != PROOF_TYPE:
            raise ConformanceError("proof type MUST equal OLPProof", code="INVALID_CORE_PROPERTY")
        if isinstance(self.version, bool) or not isinstance(self.version, int) or self.version < 0:
            raise ConformanceError("proof version MUST be a non-negative integer", code="INVALID_CORE_PROPERTY")
        if not is_semantic_identifier(self.cryptosuite):
            raise ConformanceError("cryptosuite identifier is invalid", code="INVALID_CORE_PROPERTY")
        if not is_semantic_identifier(self.proofPurpose):
            raise ConformanceError("proofPurpose identifier is invalid", code="INVALID_CORE_PROPERTY")
        if not is_absolute_uri(self.verificationMethod):
            raise ConformanceError("verificationMethod MUST be an absolute URI", code="INVALID_CORE_PROPERTY")
        if not isinstance(self.recordCommitment, RecordCommitment):
            raise ConformanceError("recordCommitment is malformed", code="INVALID_CORE_PROPERTY")
        if not isinstance(self.proofValue, bytes):
            raise ConformanceError("proofValue MUST be a byte string", code="INVALID_CORE_PROPERTY")

        if self.created is not None and not is_rfc3339(self.created):
            raise ConformanceError("created MUST be an RFC 3339 date-time with explicit offset", code="INVALID_CORE_PROPERTY")
        if self.expires is not None and not is_rfc3339(self.expires):
            raise ConformanceError("expires MUST be an RFC 3339 date-time with explicit offset", code="INVALID_CORE_PROPERTY")
        if self.domain is not None and (not isinstance(self.domain, str) or not self.domain):
            raise ConformanceError("domain MUST be a non-empty text string", code="INVALID_CORE_PROPERTY")
        if self.challenge is not None and (not isinstance(self.challenge, bytes) or not self.challenge):
            raise ConformanceError("challenge MUST be a non-empty byte string", code="INVALID_CORE_PROPERTY")
        if self.nonce is not None and (not isinstance(self.nonce, bytes) or not self.nonce):
            raise ConformanceError("nonce MUST be a non-empty byte string", code="INVALID_CORE_PROPERTY")

        if not isinstance(self.extensions, Mapping):
            raise ConformanceError("extensions MUST be a map", code="INVALID_EXTENSION_VALUE")
        for key, value in self.extensions.items():
            if not is_absolute_uri(key):
                raise ConformanceError(f"extension name MUST be an absolute URI: {key!r}", code="INVALID_EXTENSION_NAME")
            if key in CORE_PROOF_PROPERTIES:
                raise ConformanceError("extension cannot redefine a core property", code="INVALID_EXTENSION_NAME")
            validate_proof_value(value, path=f"extensions[{key!r}]")

        if len(self.critical) != len(set(self.critical)):
            raise ConformanceError("critical contains duplicate identifiers", code="INVALID_CRITICAL_DECLARATION")
        for identifier in self.critical:
            if not is_absolute_uri(identifier):
                raise ConformanceError("critical identifiers MUST be absolute URIs", code="INVALID_CRITICAL_DECLARATION")
            if identifier not in self.extensions:
                raise ConformanceError("critical identifier does not name a present extension", code="INVALID_CRITICAL_DECLARATION")
            if identifier in CORE_PROOF_PROPERTIES:
                raise ConformanceError("critical cannot name a core property", code="INVALID_CRITICAL_DECLARATION")

        # Suite-specific proof length is a v1 conformance requirement. Keeping this
        # check here lets the verifier classify malformed proof values before crypto.
        if self.version == 1 and self.cryptosuite == MANDATORY_CRYPTOSUITE and len(self.proofValue) != 64:
            raise ConformanceError("Ed25519 proofValue MUST contain exactly 64 octets", code="INVALID_PROOF_VALUE_LENGTH")

    def sorted_critical(self) -> tuple[str, ...]:
        return tuple(sorted(self.critical, key=lambda item: item.encode("utf-8")))

    def is_core_purpose(self) -> bool:
        return self.proofPurpose in CORE_PROOF_PURPOSES


def is_rfc3339(value: object) -> bool:
    if not isinstance(value, str):
        return False
    match = _RFC3339_RE.fullmatch(value)
    if not match:
        return False
    parts = {key: match.group(key) for key in ("year", "month", "day", "hour", "minute", "second", "zone")}
    year, month, day = int(parts["year"]), int(parts["month"]), int(parts["day"])
    hour, minute, second = int(parts["hour"]), int(parts["minute"]), int(parts["second"])
    if not (1 <= month <= 12 and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 60):
        return False
    if not (1 <= day <= calendar.monthrange(year, month)[1]):
        return False
    zone = parts["zone"]
    if zone not in {"Z", "z"}:
        offset_hour, offset_minute = int(zone[1:3]), int(zone[4:6])
        if offset_hour > 23 or offset_minute > 59:
            return False
    return True


def parse_rfc3339(value: str) -> datetime:
    """Parse RFC3339 for evaluation. Leap-second text maps to the following instant."""
    if not is_rfc3339(value):
        raise ConformanceError("invalid RFC 3339 date-time")
    normalized = value.replace("t", "T").replace("z", "Z")
    leap_second = normalized[17:19] == "60"
    if leap_second:
        normalized = normalized[:17] + "59" + normalized[19:]
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if leap_second:
        from datetime import timedelta

        dt += timedelta(seconds=1)
    if dt.tzinfo is None:
        raise ConformanceError("RFC 3339 date-time requires explicit offset")
    return dt.astimezone(timezone.utc)
