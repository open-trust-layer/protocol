"""Specification 0005 evidence references and relationship statement model."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import IntEnum
from types import MappingProxyType
from typing import Any

from ..encoding.deterministic_cbor import encode
from ..errors import ConformanceError, UnsupportedFeatureError
from ..values import freeze_value, is_absolute_uri, validate_record_value

RELATIONSHIP_DOMAIN = "OLP-EVIDENCE-RELATIONSHIP"
RELATIONSHIP_VERSION = 1
CORE_RELATION_TYPES = frozenset(
    {"references", "derivesFrom", "supersedes", "corrects", "disputes", "anchors", "countersigns"}
)


class EvidenceKind(IntEnum):
    RECORD = 0
    PROOF = 1


@dataclass(frozen=True, slots=True, order=True)
class EvidenceRefV1:
    kind: EvidenceKind
    identity_digest: bytes

    def __post_init__(self) -> None:
        try:
            kind = self.kind if isinstance(self.kind, EvidenceKind) else EvidenceKind(self.kind)
        except (TypeError, ValueError) as exc:
            raise ConformanceError("unsupported EvidenceRefV1 kind", code="EVIDENCE_REFERENCE_MALFORMED") from exc
        digest = bytes(self.identity_digest) if isinstance(self.identity_digest, bytearray) else self.identity_digest
        if not isinstance(digest, bytes) or len(digest) != 32:
            raise ConformanceError(
                "EvidenceRefV1 identity digest MUST contain exactly 32 octets",
                code="EVIDENCE_REFERENCE_MALFORMED",
            )
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "identity_digest", digest)

    @classmethod
    def from_value(cls, value: Any) -> "EvidenceRefV1":
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ConformanceError("EvidenceRefV1 MUST be a two-element array", code="EVIDENCE_REFERENCE_MALFORMED")
        return cls(value[0], value[1])

    def to_value(self) -> tuple[int, bytes]:
        return (int(self.kind), self.identity_digest)

    def canonical_bytes(self) -> bytes:
        return encode(self.to_value())


@dataclass(frozen=True, slots=True)
class RelationshipStatementV1:
    relation_type: str
    subject: EvidenceRefV1 | None
    objects: tuple[EvidenceRefV1, ...]
    qualifiers: Mapping[str, Any] = field(default_factory=dict)
    critical: tuple[str, ...] = ()
    version: int = RELATIONSHIP_VERSION
    domain: str = RELATIONSHIP_DOMAIN

    def __post_init__(self) -> None:
        object.__setattr__(self, "objects", tuple(self.objects))
        object.__setattr__(self, "critical", tuple(self.critical))
        if isinstance(self.qualifiers, Mapping):
            object.__setattr__(
                self,
                "qualifiers",
                MappingProxyType({key: freeze_value(value) for key, value in self.qualifiers.items()}),
            )

    @classmethod
    def from_value(cls, value: Any) -> "RelationshipStatementV1":
        if not isinstance(value, (tuple, list)) or len(value) != 7:
            raise ConformanceError(
                "RelationshipStatementV1 MUST be a seven-element array",
                code="MALFORMED_RELATIONSHIP_STATEMENT",
            )
        domain, version, relation_type, subject_raw, objects_raw, qualifiers, critical = value
        if not isinstance(objects_raw, (tuple, list)):
            raise ConformanceError("relationship objects MUST be an array", code="INVALID_RELATION_OBJECT")
        if not isinstance(critical, (tuple, list)):
            raise ConformanceError(
                "relationship critical qualifiers MUST be an array",
                code="INVALID_CRITICAL_RELATIONSHIP_QUALIFIER",
            )
        subject = None if subject_raw is None else EvidenceRefV1.from_value(subject_raw)
        objects = tuple(EvidenceRefV1.from_value(item) for item in objects_raw)
        return cls(
            domain=domain,
            version=version,
            relation_type=relation_type,
            subject=subject,
            objects=objects,
            qualifiers=qualifiers,
            critical=tuple(critical),
        )

    @classmethod
    def create(
        cls,
        relation_type: str,
        *,
        subject: EvidenceRefV1 | None,
        objects: Iterable[EvidenceRefV1],
        qualifiers: Mapping[str, Any] | None = None,
        critical: Iterable[str] = (),
    ) -> "RelationshipStatementV1":
        """Producer helper: sort set-like members before identity construction."""
        sorted_objects = tuple(sorted(tuple(objects), key=lambda ref: ref.canonical_bytes()))
        sorted_critical = tuple(sorted(tuple(critical), key=lambda item: item.encode("utf-8")))
        statement = cls(
            relation_type=relation_type,
            subject=subject,
            objects=sorted_objects,
            qualifiers=qualifiers or {},
            critical=sorted_critical,
        )
        statement.validate(
            understood_critical_qualifiers=frozenset(statement.critical),
            allow_unknown_relation=True,
        )
        return statement

    def to_value(self) -> tuple[Any, ...]:
        return (
            self.domain,
            self.version,
            self.relation_type,
            None if self.subject is None else self.subject.to_value(),
            tuple(item.to_value() for item in self.objects),
            self.qualifiers,
            self.critical,
        )

    def validate(
        self,
        *,
        understood_critical_qualifiers: frozenset[str] = frozenset(),
        allow_unknown_relation: bool = False,
    ) -> None:
        if self.domain != RELATIONSHIP_DOMAIN:
            raise ConformanceError("invalid relationship profile discriminator", code="MALFORMED_RELATIONSHIP_STATEMENT")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ConformanceError("relationship version MUST be an integer", code="MALFORMED_RELATIONSHIP_STATEMENT")
        if self.version != RELATIONSHIP_VERSION:
            raise UnsupportedFeatureError(
                "unsupported relationship version", code="UNSUPPORTED_RELATIONSHIP_VERSION"
            )
        if not isinstance(self.relation_type, str) or not self.relation_type:
            raise ConformanceError("relation type MUST be a non-empty text string", code="MALFORMED_RELATIONSHIP_STATEMENT")
        is_core = self.relation_type in CORE_RELATION_TYPES
        if not is_core and not is_absolute_uri(self.relation_type):
            raise ConformanceError(
                "extension relation type MUST be an absolute URI",
                code="MALFORMED_RELATIONSHIP_STATEMENT",
            )
        if not is_core and not allow_unknown_relation:
            raise UnsupportedFeatureError("unsupported relation type", code="UNSUPPORTED_RELATION_TYPE")

        if self.subject is not None and not isinstance(self.subject, EvidenceRefV1):
            raise ConformanceError("invalid relationship subject", code="INVALID_RELATION_SUBJECT")
        if not self.objects:
            raise ConformanceError("relationship objects MUST be non-empty", code="INVALID_RELATION_OBJECT")
        if not all(isinstance(item, EvidenceRefV1) for item in self.objects):
            raise ConformanceError("invalid relationship object", code="INVALID_RELATION_OBJECT")
        canonical = tuple(item.canonical_bytes() for item in self.objects)
        if len(set(canonical)) != len(canonical):
            raise ConformanceError("duplicate relationship object", code="DUPLICATE_RELATION_OBJECT")
        if canonical != tuple(sorted(canonical)):
            raise ConformanceError(
                "relationship objects are not canonically sorted",
                code="NON_CANONICAL_RELATION_OBJECT_ORDER",
            )

        if not isinstance(self.qualifiers, Mapping):
            raise ConformanceError("relationship qualifiers MUST be a map", code="INVALID_RELATION_QUALIFIER")
        for key, value in self.qualifiers.items():
            if not is_absolute_uri(key):
                raise ConformanceError("relationship qualifier key MUST be an absolute URI", code="INVALID_RELATION_QUALIFIER")
            validate_record_value(value, path=f"relationship.qualifiers[{key!r}]")

        if len(self.critical) != len(set(self.critical)):
            raise ConformanceError(
                "duplicate critical relationship qualifier",
                code="INVALID_CRITICAL_RELATIONSHIP_QUALIFIER",
            )
        for key in self.critical:
            if not is_absolute_uri(key) or key not in self.qualifiers:
                raise ConformanceError(
                    "critical relationship qualifier MUST name a present URI qualifier",
                    code="INVALID_CRITICAL_RELATIONSHIP_QUALIFIER",
                )
        if self.critical != tuple(sorted(self.critical, key=lambda item: item.encode("utf-8"))):
            raise ConformanceError(
                "critical relationship qualifiers are not canonically sorted",
                code="INVALID_CRITICAL_RELATIONSHIP_QUALIFIER",
            )
        unknown_critical = set(self.critical) - set(understood_critical_qualifiers)
        if unknown_critical:
            raise UnsupportedFeatureError(
                "unsupported critical relationship qualifier",
                code="UNSUPPORTED_CRITICAL_RELATIONSHIP_QUALIFIER",
            )

        self._validate_core_relation()

    def _validate_core_relation(self) -> None:
        rt = self.relation_type
        if rt == "countersigns":
            if self.subject is not None:
                raise ConformanceError("countersigns subject MUST be null", code="INVALID_RELATION_SUBJECT")
            if any(item.kind != EvidenceKind.PROOF for item in self.objects):
                raise ConformanceError(
                    "countersigns targets MUST all be ProofRef values",
                    code="COUNTERSIGNATURE_TARGET_TYPE_MISMATCH",
                )
            return

        if self.subject is None:
            raise ConformanceError("core relation requires an explicit subject", code="INVALID_RELATION_SUBJECT")

        if rt in {"supersedes", "corrects", "disputes"}:
            if self.subject.kind != EvidenceKind.RECORD or any(item.kind != EvidenceKind.RECORD for item in self.objects):
                raise ConformanceError("relation requires RecordRef subject and targets", code="INVALID_RELATION_OBJECT")
            if any(item == self.subject for item in self.objects):
                raise ConformanceError("subject cannot target itself for this relation", code="RELATION_SUBJECT_OBJECT_CONFLICT")
        elif rt == "anchors":
            if self.subject.kind != EvidenceKind.RECORD:
                raise ConformanceError("anchors subject MUST be a RecordRef", code="INVALID_RELATION_SUBJECT")
        elif rt in {"references", "derivesFrom"}:
            pass


def relationship_statement_canonical_bytes(statement: RelationshipStatementV1) -> bytes:
    statement.validate()
    return encode(statement.to_value())
