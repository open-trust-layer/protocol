"""Minimal deterministic CBOR encoder for the OLP canonical profiles.

This is intentionally not a general-purpose CBOR implementation. It supports
only the abstract value families required by Specifications 0003 and 0004 and
therefore cannot accidentally emit floats, tags, undefined, or indefinite
lengths.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..errors import EncodingError, ResourceLimitError


@dataclass(frozen=True, slots=True)
class CborLimits:
    max_depth: int = 64
    max_collection_items: int = 100_000
    max_text_bytes: int = 4 * 1024 * 1024
    max_byte_string_bytes: int = 16 * 1024 * 1024
    max_output_bytes: int = 32 * 1024 * 1024


DEFAULT_LIMITS = CborLimits()


def _head(major: int, argument: int) -> bytes:
    if argument < 0:
        raise EncodingError("CBOR argument cannot be negative")
    prefix = major << 5
    if argument < 24:
        return bytes([prefix | argument])
    if argument <= 0xFF:
        return bytes([prefix | 24, argument])
    if argument <= 0xFFFF:
        return bytes([prefix | 25]) + argument.to_bytes(2, "big")
    if argument <= 0xFFFFFFFF:
        return bytes([prefix | 26]) + argument.to_bytes(4, "big")
    if argument <= 0xFFFFFFFFFFFFFFFF:
        return bytes([prefix | 27]) + argument.to_bytes(8, "big")
    raise EncodingError("integer/length exceeds the deterministic CBOR uint64 argument range")


def encode(value: Any, *, limits: CborLimits = DEFAULT_LIMITS) -> bytes:
    """Encode *value* using the deterministic OLP CBOR profile.

    Map entries are sorted by bytewise lexicographic order of the complete
    deterministic CBOR encoding of each key, as required by OLP-CIE-1 and
    Proof Input v1.
    """

    encoded = _encode(value, limits=limits, depth=0)
    if len(encoded) > limits.max_output_bytes:
        raise ResourceLimitError("deterministic CBOR output exceeds implementation limit")
    return encoded


def _encode(value: Any, *, limits: CborLimits, depth: int) -> bytes:
    if depth > limits.max_depth:
        raise ResourceLimitError("deterministic CBOR nesting depth exceeds implementation limit")

    if value is False:
        return b"\xf4"
    if value is True:
        return b"\xf5"
    if value is None:
        return b"\xf6"

    if isinstance(value, int):
        if value >= 0:
            return _head(0, value)
        return _head(1, -1 - value)

    if isinstance(value, bytes):
        if len(value) > limits.max_byte_string_bytes:
            raise ResourceLimitError("byte string exceeds implementation limit")
        return _head(2, len(value)) + value

    if isinstance(value, str):
        try:
            raw = value.encode("utf-8", "strict")
        except UnicodeEncodeError as exc:
            raise EncodingError("text string contains non-scalar Unicode data") from exc
        if len(raw) > limits.max_text_bytes:
            raise ResourceLimitError("text string exceeds implementation limit")
        return _head(3, len(raw)) + raw

    if isinstance(value, (list, tuple)):
        if len(value) > limits.max_collection_items:
            raise ResourceLimitError("array exceeds implementation item limit")
        body = b"".join(_encode(item, limits=limits, depth=depth + 1) for item in value)
        result = _head(4, len(value)) + body
        if len(result) > limits.max_output_bytes:
            raise ResourceLimitError("deterministic CBOR output exceeds implementation limit")
        return result

    if isinstance(value, Mapping):
        if len(value) > limits.max_collection_items:
            raise ResourceLimitError("map exceeds implementation item limit")
        entries: list[tuple[bytes, bytes]] = []
        seen_encoded_keys: set[bytes] = set()
        for key, item in value.items():
            if isinstance(key, bool) or not isinstance(key, (str, int)):
                raise EncodingError("OLP deterministic CBOR map keys must be text strings or integer labels")
            key_bytes = _encode(key, limits=limits, depth=depth + 1)
            if key_bytes in seen_encoded_keys:
                raise EncodingError("duplicate canonical map key")
            seen_encoded_keys.add(key_bytes)
            value_bytes = _encode(item, limits=limits, depth=depth + 1)
            entries.append((key_bytes, value_bytes))
        entries.sort(key=lambda pair: pair[0])
        body = b"".join(key_bytes + value_bytes for key_bytes, value_bytes in entries)
        result = _head(5, len(entries)) + body
        if len(result) > limits.max_output_bytes:
            raise ResourceLimitError("deterministic CBOR output exceeds implementation limit")
        return result

    raise EncodingError(f"unsupported deterministic CBOR value type: {type(value).__name__}")
