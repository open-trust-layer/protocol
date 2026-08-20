from olp.evidence import EvidenceGraph, record_ref, relationship_record
from olp.model.evidence import EvidenceKind, EvidenceRefV1
from olp.model.record import RecordV1


def test_projection_retains_relationship_record_provenance():
    a = RecordV1(1, "claim", {"id": "a"})
    b = RecordV1(1, "claim", {"id": "b"})
    rel = relationship_record("references", subject=record_ref(a), objects=[record_ref(b)])
    graph = EvidenceGraph(records=[a, b, rel])
    assert len(graph.edges) == 1
    edge = graph.edges[0]
    assert edge.subject == record_ref(a)
    assert edge.object == record_ref(b)
    assert edge.relationship_record == record_ref(rel).identity_digest


def test_dangling_reference_does_not_invalidate_relationship():
    a = RecordV1(1, "claim", {"id": "a"})
    missing = EvidenceRefV1(EvidenceKind.RECORD, b"\x11" * 32)
    rel = relationship_record("references", subject=record_ref(a), objects=[missing])
    graph = EvidenceGraph(records=[a, rel])
    assert graph.dangling_refs() == (missing,)
    result = graph.traverse([record_ref(a)])
    assert missing in result.visited
    assert missing in result.dangling
    assert result.complete


def test_cycles_are_detected_not_rejected():
    a = RecordV1(1, "claim", {"id": "a"})
    b = RecordV1(1, "claim", {"id": "b"})
    ab = relationship_record("references", subject=record_ref(a), objects=[record_ref(b)])
    ba = relationship_record("references", subject=record_ref(b), objects=[record_ref(a)])
    graph = EvidenceGraph(records=[a, b, ab, ba])
    result = graph.traverse([record_ref(a)])
    assert result.cycles_detected
    assert {ref.identity_digest for ref in result.visited} >= {record_ref(a).identity_digest, record_ref(b).identity_digest}


def test_traversal_limit_reports_incomplete_not_invalid():
    a = RecordV1(1, "claim", {"id": "a"})
    b = RecordV1(1, "claim", {"id": "b"})
    rel = relationship_record("references", subject=record_ref(a), objects=[record_ref(b)])
    graph = EvidenceGraph(records=[a, b, rel])
    result = graph.traverse([record_ref(a)], max_depth=0)
    assert result.limit_reached
    assert not result.complete


def test_multiple_relationship_records_are_not_collapsed():
    a = RecordV1(1, "claim", {"id": "a"})
    b = RecordV1(1, "claim", {"id": "b"})
    r1 = relationship_record("references", subject=record_ref(a), objects=[record_ref(b)])
    r2 = relationship_record(
        "references",
        subject=record_ref(a),
        objects=[record_ref(b)],
        qualifiers={"https://example.org/q/context": "second"},
    )
    graph = EvidenceGraph(records=[a, b, r1, r2])
    assert len(graph.edges) == 2
    assert graph.edges[0].relationship_record != graph.edges[1].relationship_record
