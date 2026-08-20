from __future__ import annotations

import base64
import hashlib

import pytest

from olp.bundle import record_ref
from olp.encoding.record_identity import record_identity
from olp.errors import ConformanceError
from olp.model.record import RecordV1
from olp.streaming_http import (
    TransportFrameV1,
    encode_stream_frame,
    evaluate_http_operation,
    evaluate_immutable_http_read,
    evaluate_redirect,
    process_manifested_stream,
    separate_http_auth_from_olp,
    validate_content_digest,
)
from olp.transport import encode_identity_text


def _claim(subject: str) -> RecordV1:
    return RecordV1(1, "claim", {"subject": subject, "statement": "example"})


def _manifest(*records: RecordV1, profile: str = "portable") -> RecordV1:
    refs = tuple(sorted((record_ref(record) for record in records), key=lambda item: item.canonical_bytes()))
    content = (
        "OLP-EVIDENCE-BUNDLE-MANIFEST",
        1,
        profile,
        tuple(ref.to_value() for ref in refs),
        tuple(ref.to_value() for ref in refs),
        (),
        {},
        {},
        (),
    )
    return RecordV1(1, "bundle-manifest", content)


def test_stream_frame_encodes_json_sequence_and_cbor_item():
    encoded = encode_stream_frame("result", ("ok", 1, b"\x01\x02"))
    raw = bytes.fromhex(encoded["json_seq_hex"])
    assert raw.startswith(b"\x1e{")
    assert raw.endswith(b"\n")
    assert encoded["json"]["olpFrame"] == 1
    assert encoded["abstract"][:3] == ["OLP-FRAME", 1, "result"]
    assert bytes.fromhex(encoded["cbor_item_hex"])


def test_manifest_must_be_first():
    record = _claim("urn:example:alice")
    manifest = _manifest(record)
    with pytest.raises(ConformanceError) as exc:
        process_manifested_stream((TransportFrameV1("record", record), TransportFrameV1("manifest", manifest)))
    assert exc.value.code == "STREAM_MANIFEST_NOT_FIRST"


def test_record_order_after_manifest_has_no_evidence_semantics():
    first = _claim("urn:example:alice")
    second = _claim("urn:example:bob")
    manifest = _manifest(first, second)
    stream_a = (
        TransportFrameV1("manifest", manifest),
        TransportFrameV1("record", first),
        TransportFrameV1("record", second),
    )
    stream_b = (
        TransportFrameV1("manifest", manifest),
        TransportFrameV1("record", second),
        TransportFrameV1("record", first),
    )
    a = process_manifested_stream(stream_a)
    b = process_manifested_stream(stream_b)
    assert a["bundle"] == b["bundle"]
    assert a["transport_status"] == b["transport_status"] == "COMPLETE"
    assert a["frame_order_has_evidence_semantics"] is False


def test_truncation_is_incomplete_without_invalidating_present_object():
    first = _claim("urn:example:alice")
    second = _claim("urn:example:bob")
    manifest = _manifest(first, second)
    result = process_manifested_stream(
        (TransportFrameV1("manifest", manifest), TransportFrameV1("record", first)),
        truncated=True,
    )
    assert result["transport_status"] == "INCOMPLETE"
    assert result["bundle"]["closure_status"] == "INCOMPLETE"
    assert record_identity(first).hex() in result["present_record_identity_hex"]
    assert result["present_objects_remain_individually_addressable"] is True


def test_end_frame_is_optional_when_inventory_is_complete():
    record = _claim("urn:example:alice")
    manifest = _manifest(record)
    result = process_manifested_stream(
        (TransportFrameV1("manifest", manifest), TransportFrameV1("record", record))
    )
    assert result["transport_status"] == "COMPLETE"
    assert result["end_frame_present"] is False


def test_immutable_record_read_recomputes_requested_identity():
    record = _claim("urn:example:alice")
    correct = encode_identity_text("record", record_identity(record))
    success = evaluate_immutable_http_read(kind="record", requested_id_text=correct, candidate=record)
    assert success["http_status"] == 200
    assert success["identity_status"] == "MATCH"

    wrong = encode_identity_text("record", b"\x11" * 32)
    mismatch = evaluate_immutable_http_read(kind="record", requested_id_text=wrong, candidate=record)
    assert mismatch["http_status"] != 200
    assert mismatch["reason"] == "IDENTITY_MISMATCH"


def test_http_404_is_explicitly_local():
    missing = evaluate_immutable_http_read(
        kind="record",
        requested_id_text=encode_identity_text("record", b"\x22" * 32),
        candidate=None,
    )
    assert missing["http_status"] == 404
    assert missing["reason"] == "LOCAL_NOT_FOUND"
    assert missing["global_nonexistence_established"] is False


def test_http_auth_gate_prevents_storage_existence_leak():
    result = evaluate_immutable_http_read(
        kind="record",
        requested_id_text=encode_identity_text("record", b"\x22" * 32),
        candidate=None,
        authentication="MISSING",
        authorization="NOT_APPLICABLE",
    )
    assert result["http_status"] == 401
    assert result["reason"] == "HTTP_AUTHENTICATION_REQUIRED"


def test_content_negotiation_and_request_content_type_remain_http_states():
    record = _claim("urn:example:alice")
    rid = encode_identity_text("record", record_identity(record))
    not_acceptable = evaluate_immutable_http_read(
        kind="record",
        requested_id_text=rid,
        candidate=record,
        accept=("text/plain",),
    )
    assert not_acceptable["http_status"] == 406

    unsupported_request = evaluate_http_operation(
        operation="resolution",
        semantic_status="NOT_FOUND",
        content_type="text/plain",
    )
    assert unsupported_request["http_status"] == 415
    assert unsupported_request["semantic_status_evaluated"] is False


def test_resolution_not_found_is_successful_http_operation():
    result = evaluate_http_operation(
        operation="resolution",
        semantic_status="NOT_FOUND",
        content_type="application/json",
    )
    assert result["http_status"] == 200
    assert result["semantic_status"] == "NOT_FOUND"
    assert result["http_status_replaces_semantic_status"] is False


def test_self_contained_bundle_query_never_silently_downgrades():
    result = evaluate_http_operation(
        operation="bundleQuery",
        semantic_status="UNAVAILABLE",
        content_type="application/cbor",
        self_contained_required=True,
        self_contained_satisfied=False,
    )
    assert result["http_status"] == 422
    assert result["reason"] == "SELF_CONTAINED_REQUIREMENT_UNSATISFIED"
    assert result["silent_profile_downgrade"] is False


def test_content_digest_validates_http_bytes_not_evidence_identity():
    content = b'{"olp":1}'
    digest = base64.b64encode(hashlib.sha256(content).digest()).decode("ascii")
    valid = validate_content_digest(f"sha-256=:{digest}:", content, required=True)
    assert valid["status"] == "VALID"

    mismatch_digest = base64.b64encode(b"\x00" * 32).decode("ascii")
    mismatch = validate_content_digest(f"sha-256=:{mismatch_digest}:", content, required=True)
    assert mismatch["status"] == "MISMATCH"


def test_https_redirect_downgrade_and_identity_change_are_blocked():
    identity = encode_identity_text("record", b"\x33" * 32)
    downgrade = evaluate_redirect(
        method="GET",
        original_uri=f"https://example.test/v1/records/{identity}",
        location=f"http://example.test/v1/records/{identity}",
        requested_identity_text=identity,
    )
    assert downgrade == {"status": "BLOCKED", "reason": "HTTPS_DOWNGRADE", "forward_credentials": False}

    changed = evaluate_redirect(
        method="GET",
        original_uri=f"https://example.test/v1/records/{identity}",
        location="https://cdn.example.test/v1/records/r1_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        requested_identity_text=identity,
    )
    assert changed["status"] == "BLOCKED"
    assert changed["reason"] == "REDIRECT_IDENTITY_CHANGED"


def test_cross_origin_redirect_does_not_forward_credentials_by_default():
    identity = encode_identity_text("record", b"\x44" * 32)
    result = evaluate_redirect(
        method="GET",
        original_uri=f"https://one.example/v1/records/{identity}",
        location=f"https://two.example/v1/records/{identity}",
        requested_identity_text=identity,
        credentials_present=True,
    )
    assert result["status"] == "ALLOWED"
    assert result["same_origin"] is False
    assert result["forward_credentials"] is False


def test_http_authentication_never_changes_olp_proof_validity():
    result = separate_http_auth_from_olp(
        http_authentication="SUCCEEDED",
        service_authorization="ALLOWED",
        olp_cryptographic_validity="INVALID",
        olp_authority_evidence="PRESENT",
    )
    assert result["http_authentication"] == "SUCCEEDED"
    assert result["olp_cryptographic_validity"] == "INVALID"
    assert result["http_authentication_changes_olp_validity"] is False
    assert result["olp_proof_grants_http_authorization"] is False
