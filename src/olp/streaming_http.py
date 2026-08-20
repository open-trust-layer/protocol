"""Specification 0012 Milestone 24 deterministic streaming/HTTP semantics.

No function in this module performs ambient network I/O. Network-sensitive
facts are explicit inputs so streaming and HTTP security semantics remain
reproducible under conformance testing.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import urlsplit

from .bundle import PackagedResourceV1, process_bundle
from .encoding.deterministic_cbor import encode as encode_deterministic_cbor
from .encoding.proof_identity import proof_identity
from .encoding.record_identity import record_identity
from .errors import ConformanceError, ResourceLimitError, UnsupportedFeatureError
from .model.proof import OLPProof
from .model.record import RecordV1
from .transport import decode_identity_text, encode_ojve, materialize_map, project_abstract
from .values import is_absolute_uri

STREAM_FRAME_TYPES = frozenset({"manifest", "record", "proof", "resource", "result", "end"})
SINGLE_MEDIA_TYPES = ("application/cbor", "application/json")
STREAM_MEDIA_TYPES = ("application/cbor-seq", "application/json-seq")
HTTP_MAX_BODY_BYTES = 32 * 1024 * 1024
STREAM_MAX_FRAMES = 20_000
_CONTENT_DIGEST_MEMBER_RE = re.compile(
    r"^(?P<algorithm>[a-z0-9_-]+)=:(?P<value>[A-Za-z0-9+/]*={0,2}):$"
)


def _malformed(message: str, *, code: str) -> ConformanceError:
    return ConformanceError(message, code=code)


def _canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8", "strict")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise _malformed(
            "transport JSON value is not serializable scalar Unicode JSON",
            code="MALFORMED_STREAM_FRAME",
        ) from exc


@dataclass(frozen=True, slots=True)
class TransportFrameV1:
    frame_type: str
    payload: Any
    version: int = 1
    domain: str = "OLP-FRAME"

    def validate(self) -> None:
        if self.domain != "OLP-FRAME":
            raise _malformed("invalid streaming frame discriminator", code="MALFORMED_STREAM_FRAME")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise _malformed("streaming frame version must be integer", code="MALFORMED_STREAM_FRAME")
        if self.version != 1:
            raise UnsupportedFeatureError(
                "unsupported streaming frame version",
                code="UNSUPPORTED_STREAM_FRAME_VERSION",
            )
        if not isinstance(self.frame_type, str) or not self.frame_type:
            raise _malformed("streaming frame type must be non-empty text", code="MALFORMED_STREAM_FRAME")
        if self.frame_type not in STREAM_FRAME_TYPES:
            raise UnsupportedFeatureError(
                "unsupported streaming frame type",
                code="UNSUPPORTED_STREAM_FRAME_TYPE",
            )

    def to_abstract(self) -> tuple[Any, ...]:
        self.validate()
        return (self.domain, self.version, self.frame_type, self.payload)

    def to_json(self) -> dict[str, Any]:
        self.validate()
        return {"olpFrame": 1, "type": self.frame_type, "payload": encode_ojve(self.payload)}

    def to_json_seq_bytes(self) -> bytes:
        # RFC 7464 item: ASCII RS, one JSON text, LF.
        return b"\x1e" + _canonical_json_bytes(self.to_json()) + b"\n"

    def to_cbor_item(self) -> bytes:
        self.validate()
        try:
            return encode_deterministic_cbor(materialize_map(self.to_abstract()))
        except UnsupportedFeatureError:
            raise
        except Exception as exc:
            if isinstance(exc, (ConformanceError, ResourceLimitError)):
                raise
            raise UnsupportedFeatureError(
                "stream frame payload is outside the accepted deterministic CBOR subset",
                code="UNSUPPORTED_STREAM_CBOR_VALUE",
            ) from exc


def encode_stream_frame(frame_type: str, payload: Any) -> dict[str, object]:
    frame = TransportFrameV1(frame_type=frame_type, payload=payload)
    return {
        "abstract": project_abstract(frame.to_abstract()),
        "json": frame.to_json(),
        "json_seq_hex": frame.to_json_seq_bytes().hex(),
        "cbor_item_hex": frame.to_cbor_item().hex(),
    }


def encode_stream_sequence(frames: Iterable[TransportFrameV1]) -> dict[str, object]:
    frames = tuple(frames)
    if len(frames) > STREAM_MAX_FRAMES:
        raise ResourceLimitError("stream frame count exceeds implementation limit")
    for frame in frames:
        frame.validate()
    json_sequence = b"".join(frame.to_json_seq_bytes() for frame in frames)
    cbor_sequence = b"".join(frame.to_cbor_item() for frame in frames)
    return {
        "frame_count": len(frames),
        "json_seq_hex": json_sequence.hex(),
        "cbor_seq_hex": cbor_sequence.hex(),
    }


def process_manifested_stream(
    frames: Iterable[TransportFrameV1],
    *,
    truncated: bool = False,
    understood_critical_extensions: frozenset[str] = frozenset(),
) -> dict[str, object]:
    """Process an already-parsed manifested stream without semanticizing order."""

    frames = tuple(frames)
    if len(frames) > STREAM_MAX_FRAMES:
        raise ResourceLimitError("stream frame count exceeds implementation limit")
    if not frames:
        raise _malformed("manifested stream is empty", code="STREAM_MANIFEST_MISSING")
    for frame in frames:
        frame.validate()
    if frames[0].frame_type != "manifest":
        raise _malformed(
            "first manifested-bundle frame must be manifest",
            code="STREAM_MANIFEST_NOT_FIRST",
        )
    manifest = frames[0].payload
    if not isinstance(manifest, RecordV1):
        raise _malformed("manifest frame payload must be RecordV1", code="MALFORMED_STREAM_MANIFEST")

    records: list[RecordV1] = []
    proofs: list[OLPProof] = []
    resources: list[PackagedResourceV1] = []
    result_frames = 0
    end_seen = False
    manifest_count = 1

    for index, frame in enumerate(frames[1:], start=1):
        if end_seen:
            raise _malformed("semantic frame appears after end frame", code="STREAM_FRAME_AFTER_END")
        if frame.frame_type == "manifest":
            manifest_count += 1
        elif frame.frame_type == "record":
            if not isinstance(frame.payload, RecordV1):
                raise _malformed("record frame payload must be RecordV1", code="MALFORMED_STREAM_RECORD")
            records.append(frame.payload)
        elif frame.frame_type == "proof":
            if not isinstance(frame.payload, OLPProof):
                raise _malformed("proof frame payload must be OLPProof", code="MALFORMED_STREAM_PROOF")
            proofs.append(frame.payload)
        elif frame.frame_type == "resource":
            if not isinstance(frame.payload, PackagedResourceV1):
                raise _malformed("resource frame payload must be PackagedResourceV1", code="MALFORMED_STREAM_RESOURCE")
            resources.append(frame.payload)
        elif frame.frame_type == "result":
            result_frames += 1
        elif frame.frame_type == "end":
            end_seen = True
            if index != len(frames) - 1:
                raise _malformed("end frame must be final", code="STREAM_FRAME_AFTER_END")

    if manifest_count != 1:
        raise _malformed(
            "manifested stream must contain exactly one manifest frame",
            code="DUPLICATE_STREAM_MANIFEST",
        )

    bundle = process_bundle(
        manifest,
        records=records,
        proofs=proofs,
        resources=resources,
        understood_critical_extensions=understood_critical_extensions,
    )

    # Transport completeness is intentionally independent of semantic validity.
    # A fully delivered resource with a wrong digest is transport-complete while
    # bundle processing is INVALID. Unexpected/duplicate items likewise do not
    # imply truncation or missing transport bytes.
    missing_expected = bool(bundle["missing_items"] or bundle["missing_resources"])
    transport_complete = not truncated and not missing_expected

    return {
        "transport_status": "COMPLETE" if transport_complete else "INCOMPLETE",
        "truncated": bool(truncated),
        "end_frame_present": end_seen,
        "result_frame_count": result_frames,
        "bundle": bundle,
        "present_record_identity_hex": sorted(record_identity(item).hex() for item in records),
        "present_proof_identity_hex": sorted(proof_identity(item).hex() for item in proofs),
        "present_resource_digest_hex": sorted(item.ref.digest.hex() for item in resources),
        "present_objects_remain_individually_addressable": True,
        "frame_order_has_evidence_semantics": False,
    }


def negotiate_media_type(accept: Iterable[str], offered: Iterable[str]) -> str | None:
    """Negotiate already-parsed media ranges deterministically."""

    offered = tuple(offered)
    for media_range in tuple(accept):
        if not isinstance(media_range, str) or ";" in media_range:
            raise _malformed(
                "Accept fixtures must be parsed media ranges without parameters",
                code="MALFORMED_HTTP_ACCEPT",
            )
        if media_range == "*/*":
            return offered[0] if offered else None
        if media_range.endswith("/*"):
            prefix = media_range[:-1]
            for candidate in offered:
                if candidate.startswith(prefix):
                    return candidate
        elif media_range in offered:
            return media_range
    return None


def validate_content_digest(
    header_value: str | None,
    content: bytes,
    *,
    required: bool = False,
) -> dict[str, object]:
    """Validate RFC 9530 sha-256 Content-Digest over HTTP content bytes."""

    if not isinstance(content, bytes):
        raise TypeError("HTTP content must be bytes")
    if len(content) > HTTP_MAX_BODY_BYTES:
        raise ResourceLimitError("HTTP content exceeds implementation limit")
    if header_value is None:
        return {"status": "MISSING" if required else "NOT_PRESENT", "algorithm": None}
    if not isinstance(header_value, str) or not header_value.strip():
        raise _malformed("Content-Digest must be non-empty text", code="MALFORMED_CONTENT_DIGEST")

    members: dict[str, bytes] = {}
    for raw_member in header_value.split(","):
        match = _CONTENT_DIGEST_MEMBER_RE.fullmatch(raw_member.strip())
        if not match:
            raise _malformed("malformed Content-Digest member", code="MALFORMED_CONTENT_DIGEST")
        algorithm = match.group("algorithm")
        if algorithm in members:
            raise _malformed("duplicate Content-Digest algorithm", code="MALFORMED_CONTENT_DIGEST")
        encoded = match.group("value")
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise _malformed("invalid Content-Digest base64", code="MALFORMED_CONTENT_DIGEST") from exc
        if base64.b64encode(decoded).decode("ascii") != encoded:
            raise _malformed("non-canonical Content-Digest base64", code="MALFORMED_CONTENT_DIGEST")
        if algorithm == "sha-256" and len(decoded) != 32:
            raise _malformed(
                "sha-256 Content-Digest must contain exactly 32 octets",
                code="MALFORMED_CONTENT_DIGEST",
            )
        members[algorithm] = decoded

    if "sha-256" not in members:
        return {"status": "UNSUPPORTED" if required else "UNVALIDATED", "algorithm": None}
    expected = hashlib.sha256(content).digest()
    observed = members["sha-256"]
    return {
        "status": "VALID" if observed == expected else "MISMATCH",
        "algorithm": "sha-256",
        "expected_digest_hex": expected.hex(),
        "observed_digest_hex": observed.hex(),
    }


def _authorization_gate(authentication: str, authorization: str) -> tuple[int | None, str | None]:
    if authentication not in {"NOT_REQUIRED", "SUCCEEDED", "MISSING", "FAILED"}:
        raise _malformed("unknown HTTP authentication state", code="MALFORMED_HTTP_AUTH_STATE")
    if authorization not in {"NOT_APPLICABLE", "ALLOWED", "DENIED"}:
        raise _malformed("unknown HTTP authorization state", code="MALFORMED_HTTP_AUTH_STATE")
    if authentication in {"MISSING", "FAILED"}:
        return 401, "HTTP_AUTHENTICATION_REQUIRED"
    if authorization == "DENIED":
        return 403, "HTTP_AUTHORIZATION_DENIED"
    return None, None


def evaluate_immutable_http_read(
    *,
    kind: str,
    requested_id_text: str,
    candidate: RecordV1 | OLPProof | None,
    accept: Iterable[str] = SINGLE_MEDIA_TYPES,
    offered: Iterable[str] = SINGLE_MEDIA_TYPES,
    authentication: str = "NOT_REQUIRED",
    authorization: str = "NOT_APPLICABLE",
) -> dict[str, object]:
    if kind not in {"record", "proof", "bundle"}:
        raise UnsupportedFeatureError("unsupported immutable HTTP read kind", code="UNSUPPORTED_HTTP_READ_KIND")
    auth_status, auth_reason = _authorization_gate(authentication, authorization)
    if auth_status is not None:
        return {
            "http_status": auth_status,
            "reason": auth_reason,
            "authentication": authentication,
            "authorization": authorization,
            "global_nonexistence_established": False,
        }
    selected = negotiate_media_type(accept, offered)
    if selected is None:
        return {"http_status": 406, "reason": "NOT_ACCEPTABLE", "global_nonexistence_established": False}

    expected_kind = "record" if kind == "record" else "proof" if kind == "proof" else "bundle"
    _, requested_digest = decode_identity_text(requested_id_text, expected_kind=expected_kind)
    if candidate is None:
        return {
            "http_status": 404,
            "reason": "LOCAL_NOT_FOUND",
            "response_media_type": None,
            "global_nonexistence_established": False,
        }

    if kind in {"record", "bundle"}:
        if not isinstance(candidate, RecordV1):
            raise _malformed("record/bundle candidate must be RecordV1", code="MALFORMED_HTTP_CANDIDATE")
        candidate_digest = record_identity(candidate)
        message_type = "record" if kind == "record" else "bundle"
    else:
        if not isinstance(candidate, OLPProof):
            raise _malformed("proof candidate must be OLPProof", code="MALFORMED_HTTP_CANDIDATE")
        candidate_digest = proof_identity(candidate)
        message_type = "proof"

    if candidate_digest != requested_digest:
        return {
            "http_status": 422,
            "reason": "IDENTITY_MISMATCH",
            "identity_status": "MISMATCH",
            "response_media_type": None,
            "global_nonexistence_established": False,
        }
    return {
        "http_status": 200,
        "reason": None,
        "message_type": message_type,
        "identity_status": "MATCH",
        "response_media_type": selected,
        "authentication": authentication,
        "authorization": authorization,
        "global_nonexistence_established": False,
    }


def evaluate_http_operation(
    *,
    operation: str,
    semantic_status: str,
    content_type: str,
    accept: Iterable[str] = SINGLE_MEDIA_TYPES,
    offered: Iterable[str] = SINGLE_MEDIA_TYPES,
    authentication: str = "NOT_REQUIRED",
    authorization: str = "NOT_APPLICABLE",
    self_contained_required: bool = False,
    self_contained_satisfied: bool = True,
) -> dict[str, object]:
    if operation not in {"resolution", "disclosure", "bundleQuery"}:
        raise UnsupportedFeatureError("unsupported modeled HTTP operation", code="UNSUPPORTED_HTTP_OPERATION")
    auth_status, auth_reason = _authorization_gate(authentication, authorization)
    if auth_status is not None:
        return {
            "http_status": auth_status,
            "reason": auth_reason,
            "semantic_status": semantic_status,
            "semantic_status_evaluated": False,
        }
    if content_type not in SINGLE_MEDIA_TYPES:
        return {
            "http_status": 415,
            "reason": "UNSUPPORTED_MEDIA_TYPE",
            "semantic_status": semantic_status,
            "semantic_status_evaluated": False,
        }
    selected = negotiate_media_type(accept, offered)
    if selected is None:
        return {
            "http_status": 406,
            "reason": "NOT_ACCEPTABLE",
            "semantic_status": semantic_status,
            "semantic_status_evaluated": False,
        }
    if operation == "bundleQuery" and self_contained_required and not self_contained_satisfied:
        return {
            "http_status": 422,
            "reason": "SELF_CONTAINED_REQUIREMENT_UNSATISFIED",
            "semantic_status": semantic_status,
            "semantic_status_evaluated": True,
            "silent_profile_downgrade": False,
        }
    return {
        "http_status": 200,
        "reason": None,
        "message_type": {
            "resolution": "resolutionResult",
            "disclosure": "disclosureResult",
            "bundleQuery": "bundle",
        }[operation],
        "response_media_type": selected,
        "semantic_status": semantic_status,
        "semantic_status_evaluated": True,
        "http_status_replaces_semantic_status": False,
        "silent_profile_downgrade": False,
    }


def _origin(parts) -> tuple[str, str | None, int]:
    try:
        port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
    except ValueError as exc:
        raise _malformed("redirect URI contains invalid port", code="MALFORMED_HTTP_REDIRECT") from exc
    return parts.scheme.lower(), parts.hostname, port


def evaluate_redirect(
    *,
    method: str,
    original_uri: str,
    location: str,
    requested_identity_text: str | None = None,
    credentials_present: bool = False,
    allow_sensitive_post_redirect: bool = False,
    allow_cross_origin_credentials: bool = False,
) -> dict[str, object]:
    if not is_absolute_uri(original_uri) or not is_absolute_uri(location):
        raise _malformed("redirect URIs must be absolute", code="MALFORMED_HTTP_REDIRECT")
    try:
        original = urlsplit(original_uri)
        target = urlsplit(location)
        original_origin = _origin(original)
        target_origin = _origin(target)
    except ValueError as exc:
        raise _malformed("redirect URI could not be parsed safely", code="MALFORMED_HTTP_REDIRECT") from exc
    if original.scheme.lower() == "https" and target.scheme.lower() == "http":
        return {"status": "BLOCKED", "reason": "HTTPS_DOWNGRADE", "forward_credentials": False}
    if method.upper() not in {"GET", "HEAD"} and not allow_sensitive_post_redirect:
        return {
            "status": "BLOCKED",
            "reason": "SENSITIVE_METHOD_REDIRECT_BLOCKED",
            "forward_credentials": False,
        }
    if requested_identity_text is not None:
        if not isinstance(requested_identity_text, str) or not requested_identity_text:
            raise _malformed("requested identity must be non-empty", code="MALFORMED_HTTP_REDIRECT")
        if target.path.rstrip("/").rsplit("/", 1)[-1] != requested_identity_text:
            return {
                "status": "BLOCKED",
                "reason": "REDIRECT_IDENTITY_CHANGED",
                "forward_credentials": False,
            }
    same_origin = original_origin == target_origin
    return {
        "status": "ALLOWED",
        "reason": None,
        "same_origin": same_origin,
        "forward_credentials": bool(
            credentials_present and (same_origin or allow_cross_origin_credentials)
        ),
    }


def separate_http_auth_from_olp(
    *,
    http_authentication: str,
    service_authorization: str,
    olp_cryptographic_validity: str,
    olp_authority_evidence: str = "NOT_EVALUATED",
) -> dict[str, object]:
    _authorization_gate(http_authentication, service_authorization)
    for value in (olp_cryptographic_validity, olp_authority_evidence):
        if not isinstance(value, str) or not value:
            raise _malformed("OLP status must be non-empty text", code="MALFORMED_OLP_STATUS")
    return {
        "http_authentication": http_authentication,
        "service_authorization": service_authorization,
        "olp_cryptographic_validity": olp_cryptographic_validity,
        "olp_authority_evidence": olp_authority_evidence,
        "http_authentication_changes_olp_validity": False,
        "olp_proof_grants_http_authorization": False,
    }
