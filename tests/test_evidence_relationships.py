from dataclasses import replace

import pytest

from olp.evidence import parse_relationship_record, proof_ref, record_ref, relationship_record, verify_evidence_ref
from olp.encoding.record_identity import record_identity
from olp.errors import ConformanceError, UnsupportedFeatureError
from olp.model.evidence import EvidenceKind, EvidenceRefV1, RelationshipStatementV1
from olp.model.record import RecordV1


def test_record_and_proof_refs_are_typed_and_canonical(sample_record, sample_proof):
    rr = record_ref(sample_record)
    pr = proof_ref(sample_proof)
    assert rr.kind is EvidenceKind.RECORD
    assert pr.kind is EvidenceKind.PROOF
    assert len(rr.identity_digest) == len(pr.identity_digest) == 32
    assert rr.canonical_bytes() != pr.canonical_bytes()
    verify_evidence_ref(rr, sample_record)
    verify_evidence_ref(pr, sample_proof)


def test_reference_kind_and_identity_mismatch_are_distinct(sample_record, sample_proof):
    with pytest.raises(ConformanceError) as exc:
        verify_evidence_ref(record_ref(sample_record), sample_proof)
    assert exc.value.code == "EVIDENCE_KIND_MISMATCH"
    wrong = EvidenceRefV1(EvidenceKind.RECORD, b"\x00" * 32)
    with pytest.raises(ConformanceError) as exc:
        verify_evidence_ref(wrong, sample_record)
    assert exc.value.code == "EVIDENCE_IDENTITY_MISMATCH"


def test_relationship_producer_sorts_object_set(sample_record):
    a = record_ref(sample_record)
    b_record = RecordV1(1, "claim", {"value": 2})
    b = record_ref(b_record)
    rec = relationship_record("references", subject=a, objects=[b, a])
    statement = parse_relationship_record(rec)
    assert [x.canonical_bytes() for x in statement.objects] == sorted(x.canonical_bytes() for x in statement.objects)


def test_duplicate_objects_are_rejected(sample_record):
    ref = record_ref(sample_record)
    with pytest.raises(ConformanceError) as exc:
        relationship_record("references", subject=ref, objects=[ref, ref])
    assert exc.value.code == "DUPLICATE_RELATION_OBJECT"


def test_noncanonical_received_object_order_is_rejected(sample_record):
    a = record_ref(sample_record)
    b = record_ref(RecordV1(1, "claim", {"z": 2}))
    ordered = sorted((a, b), key=lambda x: x.canonical_bytes())
    statement = RelationshipStatementV1("references", ordered[0], tuple(reversed(ordered)))
    record = RecordV1(1, "evidence.relationship", statement.to_value())
    with pytest.raises(ConformanceError) as exc:
        parse_relationship_record(record)
    assert exc.value.code == "NON_CANONICAL_RELATION_OBJECT_ORDER"


@pytest.mark.parametrize("relation", ["supersedes", "corrects", "disputes"])
def test_record_only_relations_reject_proof_target(relation, sample_record, sample_proof):
    with pytest.raises(ConformanceError) as exc:
        relationship_record(relation, subject=record_ref(sample_record), objects=[proof_ref(sample_proof)])
    assert exc.value.code == "INVALID_RELATION_OBJECT"


def test_subject_object_conflict_rejected_for_supersedes(sample_record):
    ref = record_ref(sample_record)
    with pytest.raises(ConformanceError) as exc:
        relationship_record("supersedes", subject=ref, objects=[ref])
    assert exc.value.code == "RELATION_SUBJECT_OBJECT_CONFLICT"


def test_countersigns_requires_null_subject_and_proof_targets(sample_record, sample_proof):
    pr = proof_ref(sample_proof)
    rec = relationship_record("countersigns", subject=None, objects=[pr])
    assert parse_relationship_record(rec).objects == (pr,)
    with pytest.raises(ConformanceError) as exc:
        relationship_record("countersigns", subject=record_ref(sample_record), objects=[pr])
    assert exc.value.code == "INVALID_RELATION_SUBJECT"
    with pytest.raises(ConformanceError) as exc:
        relationship_record("countersigns", subject=None, objects=[record_ref(sample_record)])
    assert exc.value.code == "COUNTERSIGNATURE_TARGET_TYPE_MISMATCH"


def test_critical_qualifier_support_is_fail_closed(sample_record):
    uri = "https://example.org/qualifier/scope"
    statement = RelationshipStatementV1.create(
        "references", subject=record_ref(sample_record), objects=[record_ref(sample_record)], qualifiers={uri: "x"}, critical=[uri]
    )
    record = RecordV1(1, "evidence.relationship", statement.to_value())
    with pytest.raises(UnsupportedFeatureError) as exc:
        parse_relationship_record(record)
    assert exc.value.code == "UNSUPPORTED_CRITICAL_RELATIONSHIP_QUALIFIER"
    parsed = parse_relationship_record(record, understood_critical_qualifiers=frozenset({uri}))
    assert parsed.critical == (uri,)


def test_unknown_relation_is_unsupported_not_malformed(sample_record):
    uri = "https://example.org/relations/notarizes"
    statement = RelationshipStatementV1.create(uri, subject=record_ref(sample_record), objects=[record_ref(sample_record)])
    record = RecordV1(1, "evidence.relationship", statement.to_value())
    with pytest.raises(UnsupportedFeatureError) as exc:
        parse_relationship_record(record)
    assert exc.value.code == "UNSUPPORTED_RELATION_TYPE"
    assert parse_relationship_record(record, allow_unknown_relation=True).relation_type == uri


def test_relationship_record_identity_is_ordinary_record_identity(sample_record):
    rec = relationship_record("references", subject=record_ref(sample_record), objects=[record_ref(sample_record)])
    assert len(record_identity(rec)) == 32
