"""Milestone 24 streaming/HTTP extension of the Python reference adapter."""

from __future__ import annotations

from olp.bundle import PackagedResourceV1
from olp.model.bundle import ResourceRefV1
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
from olp.transport import project_abstract, unproject_abstract

from ..codec import proof_from_json, record_from_json
from .m23 import ReferenceAdapter as M23ReferenceAdapter

M24_STREAM_CAPABILITY = "olp.streaming-transport.v1"
M24_HTTP_CAPABILITY = "olp.http-api.v1"


def _resource_from_json(value):
    raw = value["resource_ref"]
    ref = ResourceRefV1(
        raw.get("resource_id"),
        raw["media_type"],
        raw.get("hash_algorithm", -16),
        bytes.fromhex(raw["digest_hex"]),
    )
    return PackagedResourceV1(ref=ref, content=bytes.fromhex(value["content_hex"]))


def _stream_frame_from_json(value):
    frame_type = value["type"]
    if frame_type == "manifest":
        payload = record_from_json(value["record"])
    elif frame_type == "record":
        payload = record_from_json(value["record"])
    elif frame_type == "proof":
        payload = proof_from_json(value["proof"])
    elif frame_type == "resource":
        payload = _resource_from_json(value)
    else:
        payload = unproject_abstract(value.get("payload"))
    return TransportFrameV1(
        frame_type=frame_type,
        payload=payload,
        version=value.get("version", 1),
        domain=value.get("domain", "OLP-FRAME"),
    )


class ReferenceAdapter(M23ReferenceAdapter):
    """Python reference adapter for the deterministic M24 exchange semantics."""

    def capabilities(self) -> frozenset[str]:
        return super().capabilities() | {M24_STREAM_CAPABILITY, M24_HTTP_CAPABILITY}

    def _op_encode_stream_frame(self, payload):
        abstract = unproject_abstract(payload.get("payload"))
        return encode_stream_frame(payload["frame_type"], abstract)

    def _op_process_bundle_stream(self, payload):
        frames = tuple(_stream_frame_from_json(item) for item in payload["frames"])
        return process_manifested_stream(
            frames,
            truncated=bool(payload.get("truncated", False)),
            understood_critical_extensions=frozenset(payload.get("understood_critical_extensions", ())),
        )

    def _op_evaluate_http_read(self, payload):
        kind = payload["kind"]
        raw_candidate = payload.get("candidate")
        if raw_candidate is None:
            candidate = None
        elif kind == "proof":
            candidate = proof_from_json(raw_candidate)
        else:
            candidate = record_from_json(raw_candidate)
        return evaluate_immutable_http_read(
            kind=kind,
            requested_id_text=payload["requested_id_text"],
            candidate=candidate,
            accept=tuple(payload.get("accept", ("application/cbor", "application/json"))),
            offered=tuple(payload.get("offered", ("application/cbor", "application/json"))),
            authentication=payload.get("authentication", "NOT_REQUIRED"),
            authorization=payload.get("authorization", "NOT_APPLICABLE"),
        )

    def _op_evaluate_http_operation(self, payload):
        return evaluate_http_operation(
            operation=payload["operation"],
            semantic_status=payload["semantic_status"],
            content_type=payload["content_type"],
            accept=tuple(payload.get("accept", ("application/cbor", "application/json"))),
            offered=tuple(payload.get("offered", ("application/cbor", "application/json"))),
            authentication=payload.get("authentication", "NOT_REQUIRED"),
            authorization=payload.get("authorization", "NOT_APPLICABLE"),
            self_contained_required=bool(payload.get("self_contained_required", False)),
            self_contained_satisfied=bool(payload.get("self_contained_satisfied", True)),
        )

    def _op_validate_content_digest(self, payload):
        return validate_content_digest(
            payload.get("header_value"),
            bytes.fromhex(payload.get("content_hex", "")),
            required=bool(payload.get("required", False)),
        )

    def _op_evaluate_http_redirect(self, payload):
        return evaluate_redirect(
            method=payload["method"],
            original_uri=payload["original_uri"],
            location=payload["location"],
            requested_identity_text=payload.get("requested_identity_text"),
            credentials_present=bool(payload.get("credentials_present", False)),
            allow_sensitive_post_redirect=bool(payload.get("allow_sensitive_post_redirect", False)),
            allow_cross_origin_credentials=bool(payload.get("allow_cross_origin_credentials", False)),
        )

    def _op_separate_http_auth_from_olp(self, payload):
        return separate_http_auth_from_olp(
            http_authentication=payload["http_authentication"],
            service_authorization=payload["service_authorization"],
            olp_cryptographic_validity=payload["olp_cryptographic_validity"],
            olp_authority_evidence=payload.get("olp_authority_evidence", "NOT_EVALUATED"),
        )
