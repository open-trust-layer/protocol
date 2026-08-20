"""Deterministic HTTP cache/range/limit policy helpers for Specification 0012 M24."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from .errors import ConformanceError, ResourceLimitError

DEFAULT_HTTP_REPRESENTATION_LIMIT = 32 * 1024 * 1024


def evaluate_cache_policy(
    representations: Mapping[str, bytes],
    *,
    sensitive: bool = False,
    public_cache_requested: bool = False,
    explicit_public_cache_policy: bool = False,
) -> dict[str, object]:
    """Evaluate representation-specific validator and sensitive-cache semantics.

    OLP identity is intentionally absent from strong-validator construction.
    Different JSON/CBOR bytes may represent the same OLP object, so a content
    identity digest cannot automatically serve as a strong ETag across them.
    """

    if not isinstance(representations, Mapping) or not representations:
        raise ConformanceError("representations must be a non-empty map", code="MALFORMED_HTTP_CACHE_INPUT")
    validators: dict[str, str] = {}
    bodies: list[bytes] = []
    for media_type, body in representations.items():
        if not isinstance(media_type, str) or "/" not in media_type:
            raise ConformanceError("cache representation media type is malformed", code="MALFORMED_HTTP_CACHE_INPUT")
        if not isinstance(body, bytes):
            raise ConformanceError("cache representation body must be bytes", code="MALFORMED_HTTP_CACHE_INPUT")
        if len(body) > DEFAULT_HTTP_REPRESENTATION_LIMIT:
            raise ResourceLimitError("HTTP representation exceeds implementation cache limit")
        bodies.append(body)
        validators[media_type] = '"repr-sha256-' + hashlib.sha256(body).hexdigest() + '"'

    byte_distinct = len(set(bodies)) > 1
    public_cache_allowed = not sensitive or not public_cache_requested or explicit_public_cache_policy
    return {
        "representation_etags": validators,
        "byte_distinct_representations": byte_distinct,
        "object_identity_automatically_reused_as_strong_etag": False,
        "public_cache_allowed": public_cache_allowed,
        "sensitive": bool(sensitive),
        "explicit_public_cache_policy": bool(explicit_public_cache_policy),
    }


def evaluate_range_semantics(*, partial_representation: bool, full_object_verification_requested: bool) -> dict[str, object]:
    """Keep HTTP byte-range completeness separate from OLP object verification."""

    can_verify_full_object = not partial_representation
    return {
        "partial_representation": bool(partial_representation),
        "full_object_verification_requested": bool(full_object_verification_requested),
        "can_verify_full_olp_object": can_verify_full_object,
        "verification_blocked": bool(partial_representation and full_object_verification_requested),
        "reason": "PARTIAL_REPRESENTATION_NOT_FULL_OBJECT" if partial_representation and full_object_verification_requested else None,
    }


def evaluate_http_limit(*, observed_bytes: int, max_bytes: int) -> dict[str, object]:
    if isinstance(observed_bytes, bool) or not isinstance(observed_bytes, int) or observed_bytes < 0:
        raise ConformanceError("observed_bytes must be a non-negative integer", code="MALFORMED_HTTP_LIMIT")
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
        raise ConformanceError("max_bytes must be a non-negative integer", code="MALFORMED_HTTP_LIMIT")
    exceeded = observed_bytes > max_bytes
    return {
        "http_status": 413 if exceeded else 200,
        "limit_exceeded": exceeded,
        "evidence_invalid": False,
        "observed_bytes": observed_bytes,
        "max_bytes": max_bytes,
    }


def evaluate_rate_limit(*, limited: bool, retry_after_seconds: int | None = None) -> dict[str, object]:
    if retry_after_seconds is not None and (
        isinstance(retry_after_seconds, bool)
        or not isinstance(retry_after_seconds, int)
        or retry_after_seconds < 0
    ):
        raise ConformanceError("retry_after_seconds must be a non-negative integer or null", code="MALFORMED_HTTP_RATE_LIMIT")
    return {
        "http_status": 429 if limited else 200,
        "rate_limited": bool(limited),
        "retry_after_seconds": retry_after_seconds if limited else None,
        "evidence_invalid": False,
    }
