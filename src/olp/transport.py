"""Specification 0012 deterministic transport-encoding core.

This module deliberately contains no sockets, DNS, HTTP client/server logic,
authentication, authorization, redirects, or caching.  It implements only the
transport-independent encoding boundary selected for Milestone 23:

* textual Record/Proof/Bundle identity forms;
* OLP JSON Value Encoding v1 (OJVE-1); and
* single-object OLP transport envelopes.

Transport representations never define or change OLP evidence identity.
"""

from __future__ import annotations

import base64
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .encoding.deterministic_cbor import encode as encode_deterministic_cbor
from .errors import ConformanceError, ResourceLimitError, UnsupportedFeatureError
from .values import RECORD_INT_MAX, RECORD_INT_MIN, is_absolute_uri

SAFE_JSON_INT_MAX = (1 << 53) - 1
OJVE_MAX_DEPTH = 64
OJVE_MAX_COLLECTION_ITEMS = 100_000
OJVE_MAX_TEXT_BYTES = 4 * 1024 * 1024
OJVE_MAX_BYTE_STRING_BYTES = 16 * 1024 * 1024

_IDENTITY_PREFIXES = {
    "record": "r1_",
    "proof": "p1_",
    "bundle": "b1_",
}
_PREFIX_TO_KIND = {value: key for key, value in _IDENTITY_PREFIXES.items()}
_BASE64URL_RE = re.compile(r"^[A-Za-z0-9_-]*$")
_CANONICAL_INTEGER_RE = re.compile(r"^(?:0|-[1-9][0-9]*|[1-9][0-9]*)$")

CORE_MESSAGE_TYPES = frozenset(
    {
        "record",
        "proof",
        "bundle",
        "bundleQuery",
        "resolutionRequest",
        "resolutionResult",
        "disclosureRequest",
        "disclosureResult",
        "capabilities",
        "submissionResult",
        "error",
    }
)


def _malformed(message: str, *, code: str) -> ConformanceError:
    return ConformanceError(message, code=code)


def _valid_scalar_text(value: str) -> bool:
    try:
        raw = value.encode("utf-8", "strict")
    except UnicodeEncodeError:
        return False
    return len(raw) <= OJVE_MAX_TEXT_BYTES


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode_canonical(text: str, *, expected_length: int | None = None, code: str) -> bytes:
    if not isinstance(text, str) or not _BASE64URL_RE.fullmatch(text):
        raise _malformed("base64url value contains forbidden characters or padding", code=code)
    padding = "=" * ((4 - len(text) % 4) % 4)
    try:
        decoded = base64.b64decode(text + padding, altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise _malformed("invalid base64url value", code=code) from exc
    if expected_length is not None and len(decoded) != expected_length:
        raise _malformed(f"decoded value must contain exactly {expected_length} octets", code=code)
    # Re-encoding catches non-zero/non-canonical pad bits that permissive
    # base64url decoders may otherwise accept.
    if _b64url_encode(decoded) != text:
        raise _malformed("base64url value is not canonically encoded", code=code)
    return decoded


def encode_identity_text(kind: str, digest: bytes) -> str:
    """Return the canonical textual transport form for a 32-octet identity."""

    if kind not in _IDENTITY_PREFIXES:
        raise UnsupportedFeatureError("unsupported textual identity kind", code="UNSUPPORTED_IDENTITY_KIND")
    if not isinstance(digest, bytes) or len(digest) != 32:
        raise _malformed("identity digest must contain exactly 32 octets", code="MALFORMED_IDENTITY_TEXT")
    return _IDENTITY_PREFIXES[kind] + _b64url_encode(digest)


def decode_identity_text(text: str, *, expected_kind: str | None = None) -> tuple[str, bytes]:
    """Decode a canonical ``r1_``/``p1_``/``b1_`` textual identity."""

    if not isinstance(text, str) or len(text) != 46:
        raise _malformed("textual identity must contain a 3-character prefix and 43-character body", code="MALFORMED_IDENTITY_TEXT")
    prefix = text[:3]
    kind = _PREFIX_TO_KIND.get(prefix)
    if kind is None:
        raise _malformed("unsupported or malformed textual identity prefix", code="MALFORMED_IDENTITY_TEXT")
    if expected_kind is not None:
        if expected_kind not in _IDENTITY_PREFIXES:
            raise UnsupportedFeatureError("unsupported expected textual identity kind", code="UNSUPPORTED_IDENTITY_KIND")
        if kind != expected_kind:
            raise _malformed("textual identity prefix does not match the required context", code="IDENTITY_TEXT_KIND_MISMATCH")
    digest = _b64url_decode_canonical(text[3:], expected_length=32, code="MALFORMED_IDENTITY_TEXT")
    return kind, digest


@dataclass(frozen=True, slots=True)
class OJVEMap:
    """Pair-preserving abstract map used by generic OJVE processing.

    A pair representation avoids Python-dict coercion of heterogeneous keys
    (notably ``True`` versus ``1``) and can represent array/map keys even when
    they are not hashable Python objects.
    """

    entries: tuple[tuple[Any, Any], ...]

    def __init__(self, entries: Any = ()) -> None:
        normalized = tuple((key, value) for key, value in entries)
        object.__setattr__(self, "entries", normalized)
        _validate_unique_map_keys(normalized)


def _value_token(value: Any) -> Any:
    if value is None:
        return ("null",)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, bytes):
        return ("bytes", value)
    if isinstance(value, str):
        return ("text", value)
    if isinstance(value, (tuple, list)):
        return ("array", tuple(_value_token(item) for item in value))
    if isinstance(value, OJVEMap):
        pairs = [(_value_token(key), _value_token(item)) for key, item in value.entries]
        pairs.sort(key=lambda pair: repr(pair[0]))
        return ("map", tuple(pairs))
    if isinstance(value, Mapping):
        return _value_token(OJVEMap(value.items()))
    raise _malformed(f"unsupported abstract OJVE value type {type(value).__name__}", code="MALFORMED_OJVE")


def _validate_unique_map_keys(entries: tuple[tuple[Any, Any], ...]) -> None:
    seen: set[Any] = set()
    for key, _ in entries:
        token = _value_token(key)
        if token in seen:
            raise _malformed("OJVE map contains a duplicate abstract key", code="DUPLICATE_OJVE_MAP_KEY")
        seen.add(token)


def _check_depth(depth: int) -> None:
    if depth > OJVE_MAX_DEPTH:
        raise ResourceLimitError("OJVE nesting depth exceeds implementation limit")


def _encode_ojve(value: Any, *, depth: int) -> Any:
    _check_depth(depth)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if not (RECORD_INT_MIN <= value <= RECORD_INT_MAX):
            raise _malformed("integer is outside the OLP v1 integer range", code="MALFORMED_OJVE")
        if -SAFE_JSON_INT_MAX <= value <= SAFE_JSON_INT_MAX:
            return value
        return {"$olp": "int", "v": str(value)}
    if isinstance(value, bytes):
        if len(value) > OJVE_MAX_BYTE_STRING_BYTES:
            raise ResourceLimitError("OJVE byte string exceeds implementation limit")
        return {"$olp": "bytes", "v": _b64url_encode(value)}
    if isinstance(value, bytearray):
        return _encode_ojve(bytes(value), depth=depth)
    if isinstance(value, str):
        if not _valid_scalar_text(value):
            raise _malformed("OJVE text is invalid or exceeds implementation limit", code="MALFORMED_OJVE")
        return value
    if isinstance(value, (tuple, list)):
        if len(value) > OJVE_MAX_COLLECTION_ITEMS:
            raise ResourceLimitError("OJVE array exceeds implementation item limit")
        return [_encode_ojve(item, depth=depth + 1) for item in value]
    if isinstance(value, Mapping):
        value = OJVEMap(value.items())
    if isinstance(value, OJVEMap):
        if len(value.entries) > OJVE_MAX_COLLECTION_ITEMS:
            raise ResourceLimitError("OJVE map exceeds implementation item limit")
        return {
            "$olp": "map",
            "v": [
                [_encode_ojve(key, depth=depth + 1), _encode_ojve(item, depth=depth + 1)]
                for key, item in value.entries
            ],
        }
    raise _malformed(f"unsupported abstract OJVE value type {type(value).__name__}", code="MALFORMED_OJVE")


def encode_ojve(value: Any) -> Any:
    """Encode an abstract OLP value to JSON-native OJVE-1."""

    return _encode_ojve(value, depth=0)


def _decode_ojve(value: Any, *, depth: int) -> Any:
    _check_depth(depth)
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if not (-SAFE_JSON_INT_MAX <= value <= SAFE_JSON_INT_MAX):
            raise _malformed("unsafe integer must use the OJVE integer wrapper", code="MALFORMED_OJVE")
        return value
    if isinstance(value, float):
        raise _malformed("floating-point values are outside OJVE-1", code="MALFORMED_OJVE")
    if isinstance(value, str):
        if not _valid_scalar_text(value):
            raise _malformed("OJVE text is invalid or exceeds implementation limit", code="MALFORMED_OJVE")
        return value
    if isinstance(value, list):
        if len(value) > OJVE_MAX_COLLECTION_ITEMS:
            raise ResourceLimitError("OJVE array exceeds implementation item limit")
        return tuple(_decode_ojve(item, depth=depth + 1) for item in value)
    if not isinstance(value, Mapping):
        raise _malformed(f"unsupported JSON value type {type(value).__name__}", code="MALFORMED_OJVE")

    if "$olp" not in value:
        raise _malformed("OJVE maps must use the explicit $olp map wrapper", code="MALFORMED_OJVE")
    tag = value.get("$olp")
    if not isinstance(tag, str):
        raise _malformed("OJVE wrapper tag must be text", code="MALFORMED_OJVE")
    if tag not in {"int", "bytes", "map"}:
        raise UnsupportedFeatureError("unsupported OJVE wrapper tag", code="UNSUPPORTED_OJVE_TAG")
    if set(value) != {"$olp", "v"}:
        raise _malformed("OJVE wrapper must contain exactly $olp and v", code="MALFORMED_OJVE")

    raw = value["v"]
    if tag == "int":
        if not isinstance(raw, str) or not _CANONICAL_INTEGER_RE.fullmatch(raw):
            raise _malformed("OJVE integer wrapper is not canonical decimal", code="MALFORMED_OJVE")
        number = int(raw, 10)
        if not (RECORD_INT_MIN <= number <= RECORD_INT_MAX):
            raise _malformed("integer is outside the OLP v1 integer range", code="MALFORMED_OJVE")
        return number

    if tag == "bytes":
        if not isinstance(raw, str):
            raise _malformed("OJVE byte wrapper value must be text", code="MALFORMED_OJVE")
        decoded = _b64url_decode_canonical(raw, code="MALFORMED_OJVE")
        if len(decoded) > OJVE_MAX_BYTE_STRING_BYTES:
            raise ResourceLimitError("OJVE byte string exceeds implementation limit")
        return decoded

    if not isinstance(raw, list):
        raise _malformed("OJVE map wrapper v must be an array", code="MALFORMED_OJVE")
    if len(raw) > OJVE_MAX_COLLECTION_ITEMS:
        raise ResourceLimitError("OJVE map exceeds implementation item limit")
    entries: list[tuple[Any, Any]] = []
    for entry in raw:
        if not isinstance(entry, list) or len(entry) != 2:
            raise _malformed("OJVE map entries must be [key, value] pairs", code="MALFORMED_OJVE")
        key = _decode_ojve(entry[0], depth=depth + 1)
        item = _decode_ojve(entry[1], depth=depth + 1)
        entries.append((key, item))
    return OJVEMap(entries)


def decode_ojve(value: Any) -> Any:
    """Decode JSON-native OJVE-1 to a pair-preserving abstract value."""

    return _decode_ojve(value, depth=0)


def project_abstract(value: Any) -> Any:
    """Project a generic abstract OJVE value into conformance JSON.

    This is test/adapter projection, not the OJVE wire representation.  It uses
    hexadecimal ``$bytes`` and pair-based ``$map`` to preserve all key types.
    """

    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if isinstance(value, (tuple, list)):
        return [project_abstract(item) for item in value]
    if isinstance(value, Mapping):
        value = OJVEMap(value.items())
    if isinstance(value, OJVEMap):
        return {"$map": [[project_abstract(key), project_abstract(item)] for key, item in value.entries]}
    return value


def unproject_abstract(value: Any) -> Any:
    """Decode the implementation-neutral conformance projection."""

    if isinstance(value, list):
        return tuple(unproject_abstract(item) for item in value)
    if isinstance(value, dict):
        if set(value) == {"$bytes"}:
            raw = value["$bytes"]
            if not isinstance(raw, str):
                raise _malformed("$bytes projection must contain hex text", code="MALFORMED_TRANSPORT_INPUT")
            try:
                return bytes.fromhex(raw)
            except ValueError as exc:
                raise _malformed("$bytes projection contains invalid hex", code="MALFORMED_TRANSPORT_INPUT") from exc
        if set(value) == {"$map"}:
            entries = value["$map"]
            if not isinstance(entries, list):
                raise _malformed("$map projection must contain pairs", code="MALFORMED_TRANSPORT_INPUT")
            decoded: list[tuple[Any, Any]] = []
            for entry in entries:
                if not isinstance(entry, list) or len(entry) != 2:
                    raise _malformed("$map projection entries must contain two elements", code="MALFORMED_TRANSPORT_INPUT")
                decoded.append((unproject_abstract(entry[0]), unproject_abstract(entry[1])))
            return OJVEMap(decoded)
        return OJVEMap((key, unproject_abstract(item)) for key, item in value.items())
    return value


def materialize_map(value: Any, *, allowed_key_types: tuple[type, ...] = (str, int)) -> Any:
    """Convert pair-preserving maps to ordinary mappings for object schemas.

    The conversion is deliberately explicit: generic transport maps may use
    key types that a particular OLP object model does not permit.
    """

    if isinstance(value, tuple):
        return tuple(materialize_map(item, allowed_key_types=allowed_key_types) for item in value)
    if isinstance(value, OJVEMap):
        result: dict[Any, Any] = {}
        for key, item in value.entries:
            key = materialize_map(key, allowed_key_types=allowed_key_types)
            if isinstance(key, bool) or not isinstance(key, allowed_key_types):
                raise _malformed("map key is not permitted by the target OLP object schema", code="TRANSPORT_OBJECT_KEY_TYPE_MISMATCH")
            if key in result:
                raise _malformed("duplicate key after target-object materialization", code="TRANSPORT_OBJECT_KEY_COLLISION")
            result[key] = materialize_map(item, allowed_key_types=allowed_key_types)
        return result
    return value


def _validate_message_type(message_type: Any) -> str:
    if not isinstance(message_type, str) or not _valid_scalar_text(message_type) or not message_type:
        raise _malformed("transport message type must be non-empty text", code="MALFORMED_TRANSPORT_ENVELOPE")
    if message_type not in CORE_MESSAGE_TYPES and not is_absolute_uri(message_type):
        raise _malformed("extension transport message type must be an absolute URI", code="MALFORMED_TRANSPORT_ENVELOPE")
    return message_type


@dataclass(frozen=True, slots=True)
class TransportEnvelopeV1:
    message_type: str
    payload: Any

    def __post_init__(self) -> None:
        _validate_message_type(self.message_type)

    def to_abstract(self) -> tuple[Any, ...]:
        return ("OLP-TRANSPORT", 1, self.message_type, self.payload)

    def to_json(self) -> dict[str, Any]:
        return {"olp": 1, "type": self.message_type, "payload": encode_ojve(self.payload)}

    def to_cbor(self) -> bytes:
        """Encode the abstract envelope using the existing deterministic CBOR subset.

        M23 accepts CBOR transport for values already supported by the verified
        v1 deterministic-CBOR object model.  Generic OJVE maps with key types
        outside that object model remain JSON-only in this milestone and are
        not silently narrowed.
        """

        abstract = materialize_map(self.to_abstract())
        try:
            return encode_deterministic_cbor(abstract)
        except Exception as exc:
            if isinstance(exc, (ConformanceError, ResourceLimitError, UnsupportedFeatureError)):
                raise
            raise UnsupportedFeatureError(
                "abstract transport value is outside the accepted M23 CBOR subset",
                code="UNSUPPORTED_TRANSPORT_CBOR_VALUE",
            ) from exc

    @classmethod
    def from_json(cls, value: Any) -> "TransportEnvelopeV1":
        if not isinstance(value, Mapping):
            raise _malformed("JSON transport envelope must be an object", code="MALFORMED_TRANSPORT_ENVELOPE")
        if set(value) != {"olp", "type", "payload"}:
            raise _malformed("core JSON transport envelope must contain exactly olp, type, and payload", code="MALFORMED_TRANSPORT_ENVELOPE")
        version = value["olp"]
        if isinstance(version, bool) or not isinstance(version, int):
            raise _malformed("transport envelope version must be integer", code="MALFORMED_TRANSPORT_ENVELOPE")
        if version != 1:
            raise UnsupportedFeatureError("unsupported transport envelope version", code="UNSUPPORTED_TRANSPORT_ENVELOPE_VERSION")
        message_type = _validate_message_type(value["type"])
        payload = decode_ojve(value["payload"])
        return cls(message_type=message_type, payload=payload)
