from __future__ import annotations

from dataclasses import replace

import pytest

from conftest import load_vector
from olp.encoding.record_identity import (
    blob_identity,
    definition_identity,
    record_identity,
    record_identity_bytes,
    record_identity_text,
)
from olp.errors import ConformanceError
from olp.model.record import RecordV1


def test_specification_0003_vector_exact_bytes_digest_and_text():
    vector = load_vector("0003-record-identity-v1.json")
    record = RecordV1.from_mapping(vector["record"])
    expected = vector["expected"]

    canonical = record_identity_bytes(record)
    assert len(canonical) == expected["identity_bytes_length"]
    assert canonical.hex() == expected["identity_bytes_hex"]
    assert record_identity(record).hex() == expected["record_identity_digest_hex"]
    assert record_identity_text(record) == expected["record_identity_text"]


def test_absent_and_empty_optional_fields_have_same_identity(sample_record):
    explicit = RecordV1(
        1,
        "claim",
        {"subject": "urn:example:subject:1", "statement": "example"},
        semantic_bindings={},
        profiles=(),
        relationships=(),
        extensions={},
    )
    assert record_identity(sample_record) == record_identity(explicit)


def test_profile_order_has_set_semantics(sample_record):
    a = replace(sample_record, profiles=("profile-b", "profile-a"))
    b = replace(sample_record, profiles=("profile-a", "profile-b"))
    assert record_identity(a) == record_identity(b)


def test_duplicate_profiles_rejected(sample_record):
    bad = replace(sample_record, profiles=("profile-a", "profile-a"))
    with pytest.raises(ConformanceError):
        record_identity(bad)


def test_relationship_order_is_identity_significant(sample_record):
    a = replace(sample_record, relationships=("a", "b"))
    b = replace(sample_record, relationships=("b", "a"))
    assert record_identity(a) != record_identity(b)


def test_map_insertion_order_does_not_change_identity():
    a = RecordV1(1, "claim", {"a": 1, "b": 2})
    b = RecordV1(1, "claim", {"b": 2, "a": 1})
    assert record_identity(a) == record_identity(b)


def test_exact_unicode_is_authenticated_without_normalization():
    composed = RecordV1(1, "claim", {"text": "é"})
    decomposed = RecordV1(1, "claim", {"text": "e\u0301"})
    assert record_identity(composed) != record_identity(decomposed)


def test_content_mutation_changes_identity(sample_record):
    mutated = replace(sample_record, content={"subject": "urn:example:subject:1", "statement": "different"})
    assert record_identity(sample_record) != record_identity(mutated)


def test_floating_point_content_is_rejected():
    with pytest.raises(ConformanceError):
        record_identity(RecordV1(1, "claim", {"value": 1.25}))


def test_out_of_range_record_integer_is_rejected():
    with pytest.raises(ConformanceError):
        record_identity(RecordV1(1, "claim", {"value": 1 << 64}))


def test_record_integer_boundaries_are_supported():
    record_identity(RecordV1(1, "claim", {"max": (1 << 64) - 1, "min": -(1 << 64)}))


def test_extension_names_must_be_absolute_uris(sample_record):
    bad = replace(sample_record, extensions={"vendor-extension": True})
    with pytest.raises(ConformanceError):
        record_identity(bad)


def test_unknown_top_level_mapping_field_is_rejected():
    with pytest.raises(ConformanceError):
        RecordV1.from_mapping({"envelope_version": 1, "type": "claim", "content": {}, "other": 1})


def test_textual_identity_rejects_wrong_digest_length():
    with pytest.raises(ConformanceError):
        record_identity_text(b"short")


def test_definition_identity_is_deterministic():
    a = definition_identity("urn:example:def:1", {"b": 2, "a": 1})
    b = definition_identity("urn:example:def:1", {"a": 1, "b": 2})
    assert len(a) == 32
    assert a == b


def test_blob_identity_binds_media_type():
    raw = b"same bytes"
    assert blob_identity(raw, "text/plain") != blob_identity(raw, "application/octet-stream")
    assert len(blob_identity(raw, None)) == 32


def test_record_values_are_deeply_immutable(sample_record):
    with pytest.raises(TypeError):
        sample_record.content["statement"] = "mutated"
