"""Shared OLP value validation and immutability helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, TypeAlias

from .errors import ConformanceError

OLPValue: TypeAlias = None | bool | int | bytes | str | tuple["OLPValue", ...] | Mapping[str, "OLPValue"]

_CORE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
_ABSOLUTE_URI_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:.+$", re.DOTALL)

RECORD_INT_MIN = -(1 << 64)
RECORD_INT_MAX = (1 << 64) - 1
PROOF_INT_MIN = -(1 << 63)
PROOF_INT_MAX = (1 << 63) - 1


def is_absolute_uri(value: object) -> bool:
    return isinstance(value, str) and bool(_ABSOLUTE_URI_RE.fullmatch(value)) and _valid_text(value)


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


def freeze_value(value: Any) -> Any:
    """Deep-freeze a valid-or-potential OLP abstract value without normalizing it."""

    if isinstance(value, Mapping):
        return MappingProxyType({k: freeze_value(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_value(v) for v in value)
    if isinstance(value, bytearray):
        return bytes(value)
    return value


def validate_record_value(value: Any, *, path: str = "value", depth: int = 0, max_depth: int = 64) -> None:
    """Validate the Specification 0003 abstract identity value model."""

    if depth > max_depth:
        raise ConformanceError(f"{path}: nesting depth exceeds implementation limit")

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
        for index, item in enumerate(value):
            validate_record_value(item, path=f"{path}[{index}]", depth=depth + 1, max_depth=max_depth)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not _valid_text(key):
                raise ConformanceError(f"{path}: map keys must be valid text strings")
            validate_record_value(item, path=f"{path}.{key}", depth=depth + 1, max_depth=max_depth)
        return
    raise ConformanceError(f"{path}: unsupported OLP identity value type {type(value).__name__}")


def validate_proof_value(value: Any, *, path: str = "value", depth: int = 0, max_depth: int = 64) -> None:
    """Validate the Specification 0004 Proof Input v1 value model."""

    if depth > max_depth:
        raise ConformanceError(f"{path}: nesting depth exceeds implementation limit")

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
        for index, item in enumerate(value):
            validate_proof_value(item, path=f"{path}[{index}]", depth=depth + 1, max_depth=max_depth)
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, (str, int)) or isinstance(key, bool):
                raise ConformanceError(f"{path}: Proof Input map keys must be text strings or integer labels")
            if isinstance(key, str) and not _valid_text(key):
                raise ConformanceError(f"{path}: map key is not valid Unicode scalar text")
            validate_proof_value(item, path=f"{path}.{key}", depth=depth + 1, max_depth=max_depth)
        return
    raise ConformanceError(f"{path}: unsupported Proof Input value type {type(value).__name__}")
