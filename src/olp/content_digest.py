"""Parsed RFC 9530 Content-Digest semantics for Milestone 24.

The HTTP stack is responsible for parsing RFC 8941 Structured Fields.  OLP's
M24 conformance boundary consumes the parsed dictionary meaning: an ordered
sequence of unique algorithm identifiers and byte-sequence values.  This keeps
OLP from embedding a partial second HTTP header grammar while still making the
integrity semantics independently reproducible.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from .errors import ConformanceError, ResourceLimitError

HTTP_MAX_BODY_BYTES = 32 * 1024 * 1024


def _malformed(message: str) -> ConformanceError:
    return ConformanceError(message, code="MALFORMED_CONTENT_DIGEST")


def validate_parsed_content_digest(
    members: Iterable[tuple[str, bytes]] | None,
    content: bytes,
    *,
    required: bool = False,
) -> dict[str, object]:
    """Validate parsed RFC 9530 digest members over the actual HTTP content.

    ``members`` is ``None`` when the field is absent. Each tuple represents one
    already-parsed RFC 8941 dictionary member whose value was a Byte Sequence.
    Unknown algorithms remain representable; M24 requires SHA-256 support and
    does not reinterpret transport integrity as OLP evidence validity.
    """

    if not isinstance(content, bytes):
        raise TypeError("HTTP content must be bytes")
    if len(content) > HTTP_MAX_BODY_BYTES:
        raise ResourceLimitError("HTTP content exceeds implementation limit")
    if members is None:
        return {"status": "MISSING" if required else "NOT_PRESENT", "algorithm": None}

    normalized: dict[str, bytes] = {}
    for algorithm, digest in members:
        if not isinstance(algorithm, str) or not algorithm:
            raise _malformed("Content-Digest algorithm must be non-empty text")
        # RFC 8941 parsing has already validated the Structured Fields key
        # grammar. The semantic layer still rejects duplicate parsed members.
        if algorithm in normalized:
            raise _malformed("duplicate Content-Digest algorithm")
        if not isinstance(digest, bytes):
            raise _malformed("Content-Digest member value must be parsed bytes")
        if algorithm == "sha-256" and len(digest) != 32:
            raise _malformed("sha-256 Content-Digest must contain exactly 32 octets")
        normalized[algorithm] = digest

    if "sha-256" not in normalized:
        return {"status": "UNSUPPORTED" if required else "UNVALIDATED", "algorithm": None}

    expected = hashlib.sha256(content).digest()
    observed = normalized["sha-256"]
    return {
        "status": "VALID" if observed == expected else "MISMATCH",
        "algorithm": "sha-256",
        "expected_digest_hex": expected.hex(),
        "observed_digest_hex": observed.hex(),
    }
