"""Shared OLP value validation, URI syntax guards, and immutability helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, TypeAlias

from .errors import ConformanceError, ResourceLimitError

OLPValue: TypeAlias = None | bool | int | bytes | str | tuple["OLPValue", ...] | Mapping[str, "OLPValue"]

_CORE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*$")
_URI_ALLOWED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;=%"
)
_HEX = frozenset("0123456789abcdefABCDEF")

RECORD_INT_MIN = -(1 << 64)
RECORD_INT_MAX = (1 << 64) - 1
PROOF_INT_MIN = -(1 << 63)
PROOF_INT_MAX = (1 << 63) - 1

# Reference implementation resource profile. These are implementation limits,
# not additional abstract protocol constraints. They intentionally match the
# deterministic-CBOR defaults so hostile objects are bounded before freezing
# recursively or allocating canonical output.
VALUE_MAX_DEPTH = 64
VALUE_MAX_COLLECTION_ITEMS = 100_000
VALUE_MAX_TEXT_BYTES = 4 * 1024 * 1024
VALUE_MAX_BYTE_STRING_BYTES = 16 * 1024 * 1024


def is_absolute_uri(value: object) -> bool:
    """Return whether *value* is a syntactically absolute RFC 3986 URI.

    OLP authenticates the exact URI string and performs no URI normalization.
    This guard therefore checks only generic URI syntax: a valid scheme, the
    RFC 3986 ASCII character repertoire, and complete percent-encoding
    triplets. Scheme-specific semantics are deliberately out of scope.
    """

    if not isinstance(value, str) or not _valid_text(value):
        return False
    scheme, separator, remainder = value.partition(":")
    if not separator or not _URI_SCHEME_RE.fullmatch(scheme):
        return False
    # RFC 3986 URI syntax is expressed over the US-ASCII character set.
    # Non-ASCII identifying data must be percent-encoded by the URI producer.
    i = 0
    while i < len(remainder):
        char = remainder[i]
        if ord(char) > 0x7F or char not in _URI_ALLOWED:
            return False
        if char == "%":
            if i + 2 >= len(remainder) or remainder[i + 1] not in _HEX or remainder[i + 2] not in _HEX:
                return False
            i += 3
            continue
        i += 1
    return True


def is_semantic_identifier(value: object) -> bool:
    if not isinstance(value, str) or not _valid_text(value):
        return False
    return bool(_CORE_IDENTIFIER_RE.fullmatch(value)) or is_absolute_uri(value)


def _valid_text(value: str) -> bool:
    try:
        value.encode("utf-8", "strict")
    except UnicodeEncodeError:
        return False
    return True


def _check_scalar_resource_limits(value: Any, *, path: str) -> None:
    if isinstance(value, (bytes, bytearray)) and len(value) > VALUE_MAX_BYTE_STRING_BYTES:
        raise ResourceLimitError(f"{path}: byte string exceeds implementation limit")
    if isinstance(value, str):
        try:
            raw = value.encode("utf-8", "strict")
        except UnicodeEncodeError:
            return
        if len(raw) > VALUE_MAX_TEXT_BYTES:
            raise ResourceLimitError(f"{path}: text string exceeds implementation limit")


def freeze_value(
    value: Any,
    *,
    path: str = "value",
    depth: int = 0,
    max_depth: int = VALUE_MAX_DEPTH,
    max_collection_items: int = VALUE_MAX_COLLECTION_ITEMS,
) -> Any:
    """Deep-freeze an OLP value while enforcing pre-allocation resource bounds.

    Validation still decides whether a value is semantically permitted. This
    helper's job is to ensure immutability cannot itself become an unbounded
    recursive/allocation step on hostile input.
    """

    if depth > max_depth:
        raise ResourceLimitError(f"{path}: nesting depth exceeds implementation limit")
    _check_scalar_resource_limits(value, path=path)

    if isinstance(value, Mapping):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: map exceeds implementation item limit")
        return MappingProxyType(
            {
                key: freeze_value(
                    item,
                    path=f"{path}.{key}",
                    depth=depth + 1,
                    max_depth=max_depth,
                    max_collection_items=max_collection_items,
                )
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: array exceeds implementation item limit")
        return tuple(
            freeze_value(
                item,
                path=f"{path}[{index}]",
                depth=depth + 1,
                max_depth=max_depth,
                max_collection_items=max_collection_items,
            )
            for index, item in enumerate(value)
        )
    if isinstance(value, bytearray):
        return bytes(value)
    return value


def validate_record_value(
    value: Any,
    *,
    path: str = "value",
    depth: int = 0,
    max_depth: int = VALUE_MAX_DEPTH,
    max_collection_items: int = VALUE_MAX_COLLECTION_ITEMS,
) -> None:
    """Validate the Specification 0003 abstract identity value model."""

    if depth > max_depth:
        raise ResourceLimitError(f"{path}: nesting depth exceeds implementation limit")
    _check_scalar_resource_limits(value, path=path)

    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not (RECORD_INT_MIN <= value <= RECORD_INT_MAX):
            raise ConformanceError(f"{path}: integer is outside the OLP-CIE-1 v1 range")
        return
    if isinstance(value, bytes):
        return
    if isinstance(value, str):
        if not _valid_text(value):
            raise ConformanceError(f"{path}: text is not valid Unicode scalar text")
        return
    if isinstance(value, (tuple, list)):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: array exceeds implementation item limit")
        for index, item in enumerate(value):
            validate_record_value(
                item,
                path=f"{path}[{index}]",
                depth=depth + 1,
                max_depth=max_depth,
                max_collection_items=max_collection_items,
            )
        return
    if isinstance(value, Mapping):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: map exceeds implementation item limit")
        for key, item in value.items():
            if not isinstance(key, str) or not _valid_text(key):
                raise ConformanceError(f"{path}: map keys must be valid text strings")
            validate_record_value(
                item,
                path=f"{path}.{key}",
                depth=depth + 1,
                max_depth=max_depth,
                max_collection_items=max_collection_items,
            )
        return
    raise ConformanceError(f"{path}: unsupported OLP identity value type {type(value).__name__}")


def validate_proof_value(
    value: Any,
    *,
    path: str = "value",
    depth: int = 0,
    max_depth: int = VALUE_MAX_DEPTH,
    max_collection_items: int = VALUE_MAX_COLLECTION_ITEMS,
) -> None:
    """Validate the Specification 0004 Proof Input v1 value model."""

    if depth > max_depth:
        raise ResourceLimitError(f"{path}: nesting depth exceeds implementation limit")
    _check_scalar_resource_limits(value, path=path)

    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if not (PROOF_INT_MIN <= value <= PROOF_INT_MAX):
            raise ConformanceError(f"{path}: integer is outside the Proof Input v1 range")
        return
    if isinstance(value, bytes):
        return
    if isinstance(value, str):
        if not _valid_text(value):
            raise ConformanceError(f"{path}: text is not valid Unicode scalar text")
        return
    if isinstance(value, (tuple, list)):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: array exceeds implementation item limit")
        for index, item in enumerate(value):
            validate_proof_value(
                item,
                path=f"{path}[{index}]",
                depth=depth + 1,
                max_depth=max_depth,
                max_collection_items=max_collection_items,
            )
        return
    if isinstance(value, Mapping):
        if len(value) > max_collection_items:
            raise ResourceLimitError(f"{path}: map exceeds implementation item limit")
        for key, item in value.items():
            if not isinstance(key, (str, int)) or isinstance(key, bool):
                raise ConformanceError(f"{path}: Proof Input map keys must be text strings or integer labels")
            if isinstance(key, str) and not _valid_text(key):
                raise ConformanceError(f"{path}: map key is not valid Unicode scalar text")
            validate_proof_value(
                item,
                path=f"{path}.{key}",
                depth=depth + 1,
                max_depth=max_depth,
                max_collection_items=max_collection_items,
            )
        return
    raise ConformanceError(f"{path}: unsupported Proof Input value type {type(value).__name__}")
