from __future__ import annotations

import base64
import hashlib

import pytest

from olp.bundle import PackagedResourceV1
from olp.errors import ConformanceError
from olp.http_policy import (
    evaluate_cache_policy,
    evaluate_http_limit,
    evaluate_range_semantics,
    evaluate_rate_limit,
)
from olp.model.bundle import ResourceRefV1
from olp.model.record import RecordV1
from olp.streaming_http import TransportFrameV1, evaluate_redirect, process_manifested_stream, validate_content_digest


def _resource_manifest(ref: ResourceRefV1) -> RecordV1:
    return RecordV1(
        1,
        "bundle-manifest",
        (
            "OLP-EVIDENCE-BUNDLE-MANIFEST",
            1,
            "portable",
            (),
            (),
            (ref.to_value(),),
            {},
            {},
            (),
        ),
    )


def test_complete_stream_remains_transport_complete_when_resource_is_invalid():
    expected_digest = hashlib.sha256(b"expected").digest()
    ref = ResourceRefV1(None, "application/octet-stream", -16, expected_digest)
    manifest = _resource_manifest(ref)
    invalid_resource = PackagedResourceV1(ref=ref, content=b"tampered")

    result = process_manifested_stream(
        (
            TransportFrameV1("manifest", manifest),
            TransportFrameV1("resource", invalid_resource),
        )
    )

    assert result["transport_status"] == "COMPLETE"
    assert result["bundle"]["status"] == "INVALID"
    assert result["bundle"]["resource_errors"][0]["reason"] == "RESOURCE_DIGEST_MISMATCH"


def test_sha256_content_digest_requires_exact_32_octets():
    short_digest = base64.b64encode(b"short").decode("ascii")
    with pytest.raises(ConformanceError) as exc:
        validate_content_digest(f"sha-256=:{short_digest}:", b"payload", required=True)
    assert exc.value.code == "MALFORMED_CONTENT_DIGEST"


def test_malformed_redirect_port_fails_closed():
    with pytest.raises(ConformanceError) as exc:
        evaluate_redirect(
            method="GET",
            original_uri="https://example.test:99999/v1/records/r1_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            location="https://example.test/v1/records/r1_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            requested_identity_text="r1_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        )
    assert exc.value.code == "MALFORMED_HTTP_REDIRECT"


def test_representation_specific_etags_do_not_reuse_object_identity():
    result = evaluate_cache_policy(
        {
            "application/json": b'{"olp":1}',
            "application/cbor": b"\x84\x01",
        }
    )
    assert result["byte_distinct_representations"] is True
    assert result["representation_etags"]["application/json"] != result["representation_etags"]["application/cbor"]
    assert result["object_identity_automatically_reused_as_strong_etag"] is False


def test_sensitive_public_cache_requires_explicit_policy():
    blocked = evaluate_cache_policy(
        {"application/json": b"sensitive"},
        sensitive=True,
        public_cache_requested=True,
        explicit_public_cache_policy=False,
    )
    assert blocked["public_cache_allowed"] is False

    allowed = evaluate_cache_policy(
        {"application/json": b"sensitive"},
        sensitive=True,
        public_cache_requested=True,
        explicit_public_cache_policy=True,
    )
    assert allowed["public_cache_allowed"] is True


def test_partial_range_cannot_be_verified_as_full_olp_object():
    result = evaluate_range_semantics(
        partial_representation=True,
        full_object_verification_requested=True,
    )
    assert result["can_verify_full_olp_object"] is False
    assert result["verification_blocked"] is True
    assert result["reason"] == "PARTIAL_REPRESENTATION_NOT_FULL_OBJECT"


def test_http_size_limit_never_becomes_invalid_evidence():
    result = evaluate_http_limit(observed_bytes=1025, max_bytes=1024)
    assert result["http_status"] == 413
    assert result["limit_exceeded"] is True
    assert result["evidence_invalid"] is False


def test_http_rate_limit_never_becomes_invalid_evidence():
    result = evaluate_rate_limit(limited=True, retry_after_seconds=30)
    assert result["http_status"] == 429
    assert result["retry_after_seconds"] == 30
    assert result["evidence_invalid"] is False
