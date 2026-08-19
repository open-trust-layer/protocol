"""OLP-CI-1 Record Identity and related Specification 0003 identities."""

from __future__ import annotations

import base64
import hashlib
from typing import Any

from ..constants import RECORD_TEXT_PREFIX
from ..errors import ConformanceError
from ..model.record import RecordV1
from ..values import is_semantic_identifier, validate_record_value
from .deterministic_cbor import CborLimits, DEFAULT_LIMITS, encode


def record_identity_bytes(record: RecordV1, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    """Return the exact OLP-CIE-1 bytes of the OLP-CI-1 record preimage."""
    return encode(record.identity_preimage(), limits=limits)


def record_identity(record: RecordV1, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    """Return the authoritative 32-byte OLP-CI-1 SHA-256 digest."""
    return hashlib.sha256(record_identity_bytes(record, limits=limits)).digest()


def record_identity_text(record_or_digest: RecordV1 | bytes) -> str:
    """Return the canonical Specification 0012 presentation r1_<base64url-no-padding>."""
    digest = record_identity(record_or_digest) if isinstance(record_or_digest, RecordV1) else record_or_digest
    if not isinstance(digest, bytes) or len(digest) != 32:
        raise ConformanceError("Record Identity digest MUST contain exactly 32 octets")
    encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return RECORD_TEXT_PREFIX + encoded


def definition_identity(semantic_identifier: str, definition_value: Any) -> bytes:
    if not is_semantic_identifier(semantic_identifier):
        raise ConformanceError("definition semantic identifier is invalid")
    validate_record_value(definition_value, path="definitionValue")
    preimage = ("OLP-DEFINITION", 1, semantic_identifier, definition_value)
    return hashlib.sha256(encode(preimage)).digest()


def blob_identity(raw_blob: bytes, media_type: str | None = None) -> bytes:
    if not isinstance(raw_blob, bytes):
        raise ConformanceError("raw blob MUST be a byte string")
    if media_type is not None and (not isinstance(media_type, str) or not media_type):
        raise ConformanceError("media type MUST be null or a non-empty text string")
    preimage = ("OLP-BLOB", 1, media_type, raw_blob)
    return hashlib.sha256(encode(preimage)).digest()
