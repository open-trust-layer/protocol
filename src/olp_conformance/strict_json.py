"""Strict JSON helpers for the executable conformance boundary.

The adapter contract is security-sensitive test infrastructure: accepting a
JSON object differently in Python and Rust would make the conformance judge
ambiguous.  These helpers reject duplicate names, non-standard numeric values,
floating point, excessive input, excessive structural nesting, and lone
Unicode surrogates before protocol operations run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 128
I128_MIN = -(1 << 127)
I128_MAX = (1 << 127) - 1


class StrictJSONError(ValueError):
    pass


def _reject_float(_: str) -> Any:
    raise StrictJSONError("floating-point JSON numbers are outside the OLP adapter profile")


def _reject_constant(value: str) -> Any:
    raise StrictJSONError(f"non-standard JSON numeric constant is forbidden: {value}")


def _parse_int(value: str) -> int:
    number = int(value, 10)
    if not (I128_MIN <= number <= I128_MAX):
        raise StrictJSONError("JSON integer outside adapter i128 range")
    return number


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate JSON property {key!r}")
        result[key] = value
    return result


def _preflight_depth(text: str, *, max_depth: int) -> None:
    depth = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > max_depth:
                raise StrictJSONError("JSON nesting depth exceeds adapter limit")
        elif char in "]}":
            depth -= 1
            if depth < 0:
                # json.loads will provide the precise syntax error; avoid letting
                # malformed input defeat the depth preflight.
                depth = 0


def _validate_scalar_text(value: Any) -> None:
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            try:
                item.encode("utf-8", "strict")
            except UnicodeEncodeError as exc:
                raise StrictJSONError("JSON string contains non-scalar Unicode data") from exc
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())


def loads(text: str, *, max_bytes: int = MAX_JSON_BYTES, max_depth: int = MAX_JSON_DEPTH) -> Any:
    if not isinstance(text, str):
        raise TypeError("strict JSON input must be text")
    try:
        encoded = text.encode("utf-8", "strict")
    except UnicodeEncodeError as exc:
        raise StrictJSONError("JSON input contains non-scalar Unicode data") from exc
    if len(encoded) > max_bytes:
        raise StrictJSONError("JSON input exceeds adapter size limit")
    _preflight_depth(text, max_depth=max_depth)
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_float=_reject_float,
            parse_int=_parse_int,
            parse_constant=_reject_constant,
        )
    except StrictJSONError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise StrictJSONError(str(exc)) from exc
    _validate_scalar_text(value)
    return value


def load_path(path: str | Path) -> Any:
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        raise StrictJSONError(f"JSON file exceeds adapter size limit: {path}")
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise StrictJSONError(f"JSON file is not valid UTF-8: {path}") from exc
    return loads(text)
