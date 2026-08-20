"""Executable Specification 0005 evidence relationship and graph helpers."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, Mapping

from .encoding.proof_identity import proof_identity
from .encoding.record_identity import record_identity
from .errors import ConformanceError, UnsupportedFeatureError
from .model.evidence import EvidenceKind, EvidenceRefV1, RelationshipStatementV1
from .model.proof import OLPProof
from .model.record import RecordV1

RELATIONSHIP_RECORD_TYPE = "evidence.relationship"


def record_ref(record: RecordV1) -> EvidenceRefV1:
    return EvidenceRefV1(EvidenceKind.RECORD, record_identity(record))


def proof_ref(proof: OLPProof) -> EvidenceRefV1:
    return EvidenceRefV1(EvidenceKind.PROOF, proof_identity(proof))


def verify_evidence_ref(reference: EvidenceRefV1, evidence: RecordV1 | OLPProof) -> None:
    if isinstance(evidence, RecordV1):
        actual_kind = EvidenceKind.RECORD
        actual = record_identity(evidence)
    elif isinstance(evidence, OLPProof):
        actual_kind = EvidenceKind.PROOF
        actual = proof_identity(evidence)
    else:
        raise ConformanceError("unsupported evidence object", code="EVIDENCE_KIND_MISMATCH")
    if actual_kind != reference.kind:
        raise ConformanceError("evidence object kind does not match reference", code="EVIDENCE_KIND_MISMATCH")
    if actual != reference.identity_digest:
        raise ConformanceError("evidence identity does not match reference", code="EVIDENCE_IDENTITY_MISMATCH")


def relationship_record(
    relation_type: str,
    *,
    subject: EvidenceRefV1 | None,
    objects: Iterable[EvidenceRefV1],
    qualifiers: Mapping[str, object] | None = None,
    critical: Iterable[str] = (),
    record_type: str = RELATIONSHIP_RECORD_TYPE,
) -> RecordV1:
    statement = RelationshipStatementV1.create(
        relation_type,
        subject=subject,
        objects=objects,
        qualifiers=qualifiers,
        critical=critical,
    )
    return RecordV1(envelope_version=1, type=record_type, content=statement.to_value())


def parse_relationship_record(
    record: RecordV1,
    *,
    understood_critical_qualifiers: frozenset[str] = frozenset(),
    allow_unknown_relation: bool = False,
) -> RelationshipStatementV1:
    record.validate()
    statement = RelationshipStatementV1.from_value(record.content)
    statement.validate(
        understood_critical_qualifiers=understood_critical_qualifiers,
        allow_unknown_relation=allow_unknown_relation,
    )
    enclosing = record_identity(record)
    refs = (() if statement.subject is None else (statement.subject,)) + statement.objects
    if any(ref.kind == EvidenceKind.RECORD and ref.identity_digest == enclosing for ref in refs):
        raise ConformanceError(
            "relationship record MUST NOT self-reference its own Record Identity",
            code="RELATION_SUBJECT_OBJECT_CONFLICT",
        )
    return statement


@dataclass(frozen=True, slots=True)
class ProjectedEdge:
    subject: EvidenceRefV1 | None
    relation_type: str
    object: EvidenceRefV1
    relationship_record: bytes


@dataclass(frozen=True, slots=True)
class TraversalResult:
    visited: tuple[EvidenceRefV1, ...]
    traversed_edges: tuple[ProjectedEdge, ...]
    dangling: tuple[EvidenceRefV1, ...]
    complete: bool
    limit_reached: bool
    cycles_detected: bool


class EvidenceGraph:
    """Finite local reified evidence graph. No resolver or trust policy is hidden inside it."""

    def __init__(self, *, records: Iterable[RecordV1] = (), proofs: Iterable[OLPProof] = ()) -> None:
        self.records: dict[EvidenceRefV1, RecordV1] = {}
        self.proofs: dict[EvidenceRefV1, OLPProof] = {}
        self.relationships: list[tuple[RecordV1, RelationshipStatementV1]] = []
        self.edges: tuple[ProjectedEdge, ...] = ()
        for record in records:
            self.add_record(record)
        for proof in proofs:
            self.add_proof(proof)
        self._rebuild_projection()

    def add_record(self, record: RecordV1) -> EvidenceRefV1:
        ref = record_ref(record)
        prior = self.records.get(ref)
        if prior is not None and prior != record:
            raise ConformanceError("conflicting records share an identity", code="IDENTITY_COLLISION_OR_CONFLICT")
        self.records[ref] = record
        try:
            statement = parse_relationship_record(record)
        except UnsupportedFeatureError:
            statement = None
        except ConformanceError:
            statement = None
        if statement is not None and not any(existing_ref == ref for existing_ref, _ in self._relationship_refs()):
            self.relationships.append((record, statement))
        return ref

    def add_proof(self, proof: OLPProof) -> EvidenceRefV1:
        ref = proof_ref(proof)
        prior = self.proofs.get(ref)
        if prior is not None and prior != proof:
            raise ConformanceError("conflicting proofs share an identity", code="IDENTITY_COLLISION_OR_CONFLICT")
        self.proofs[ref] = proof
        return ref

    def _relationship_refs(self):
        for record, statement in self.relationships:
            yield record_ref(record), statement

    def _rebuild_projection(self) -> None:
        edges: list[ProjectedEdge] = []
        for record, statement in self.relationships:
            relationship_id = record_identity(record)
            for target in statement.objects:
                edges.append(ProjectedEdge(statement.subject, statement.relation_type, target, relationship_id))
        edges.sort(
            key=lambda edge: (
                b"" if edge.subject is None else edge.subject.canonical_bytes(),
                edge.relation_type.encode("utf-8"),
                edge.object.canonical_bytes(),
                edge.relationship_record,
            )
        )
        self.edges = tuple(edges)

    def rebuild(self) -> None:
        self.relationships = []
        for record in self.records.values():
            try:
                statement = parse_relationship_record(record)
            except (ConformanceError, UnsupportedFeatureError):
                continue
            self.relationships.append((record, statement))
        self._rebuild_projection()

    def resolve_local(self, reference: EvidenceRefV1) -> RecordV1 | OLPProof | None:
        return self.records.get(reference) if reference.kind == EvidenceKind.RECORD else self.proofs.get(reference)

    def dangling_refs(self) -> tuple[EvidenceRefV1, ...]:
        refs: set[EvidenceRefV1] = set()
        for _, statement in self.relationships:
            if statement.subject is not None:
                refs.add(statement.subject)
            refs.update(statement.objects)
        return tuple(sorted((ref for ref in refs if self.resolve_local(ref) is None), key=lambda ref: ref.canonical_bytes()))

    def traverse(
        self,
        roots: Iterable[EvidenceRefV1],
        *,
        max_depth: int = 32,
        max_nodes: int = 10_000,
        relation_types: frozenset[str] | None = None,
    ) -> TraversalResult:
        if max_depth < 0 or max_nodes < 1:
            raise ValueError("traversal limits must be non-negative depth and positive node count")
        outgoing: dict[EvidenceRefV1, list[ProjectedEdge]] = defaultdict(list)
        for edge in self.edges:
            if edge.subject is not None and (relation_types is None or edge.relation_type in relation_types):
                outgoing[edge.subject].append(edge)
        for bucket in outgoing.values():
            bucket.sort(key=lambda edge: (edge.relation_type.encode("utf-8"), edge.object.canonical_bytes(), edge.relationship_record))

        queue = deque((root, 0) for root in sorted(set(roots), key=lambda ref: ref.canonical_bytes()))
        visited: set[EvidenceRefV1] = set()
        ordered: list[EvidenceRefV1] = []
        traversed: list[ProjectedEdge] = []
        dangling: set[EvidenceRefV1] = set()
        limit_reached = False
        cycles = False
        while queue:
            ref, depth = queue.popleft()
            if ref in visited:
                cycles = True
                continue
            if len(visited) >= max_nodes:
                limit_reached = True
                break
            visited.add(ref)
            ordered.append(ref)
            if self.resolve_local(ref) is None:
                dangling.add(ref)
            if depth >= max_depth:
                if outgoing.get(ref):
                    limit_reached = True
                continue
            for edge in outgoing.get(ref, ()):
                traversed.append(edge)
                if edge.object in visited:
                    cycles = True
                else:
                    queue.append((edge.object, depth + 1))
        return TraversalResult(
            visited=tuple(ordered),
            traversed_edges=tuple(traversed),
            dangling=tuple(sorted(dangling, key=lambda ref: ref.canonical_bytes())),
            complete=not limit_reached,
            limit_reached=limit_reached,
            cycles_detected=cycles,
        )
