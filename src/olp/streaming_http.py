"""Specification 0012 Milestone 24 deterministic streaming/HTTP semantics.

This module deliberately performs no ambient network I/O.  It models the
security-sensitive semantics of OLP sequence transport and HTTP exchange from
caller-supplied frames, objects, bytes, and policy state so conformance remains
fully reproducible.

The module keeps independent dimensions independent:

* stream completeness is not object validity;
* HTTP status is not an OLP semantic result;
* HTTP authentication is not OLP proof validity or authority evidence;
* Content-Digest protects HTTP content bytes, not OLP evidence identity;
* local HTTP 404 does not establish global nonexistence; and
* redirect permission never changes an identity-bearing retrieval target.
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
from .model.bundle import ResourceRefV1
from .model.proof import OLPProof
from .model.record import RecordV1
from .transport import (
    OJVEMap,
    decode_identity_text,
    encode_ojve,
    materialize_map,
    project_abstract,
)
from .values import is_absolute_uri

STREAM_FRAME_TYPES = frozenset({"manifest", "record", "proof", "resource", "result", "end"})
SINGLE_MEDIA_TYPES = ("application/cbor", "application/json")
STREAM_MEDIA_TYPES = ("application/cbor-seq", "application/json-seq")
HTTP_MAX_BODY_BYTES = 32 * 1024 * 1024
STREAM_MAX_FRAMES = 20_000

_CONTENT_DIGEST_MEMBER_RE = re.compile(r"^(?P<algorithm>[a-z0-9_-]+)=:(?P<value>[A-Za-z0-9+/]*={0,2}):$")


def _malformed(message: str, *, code: str) -> ConformanceError:
    return ConformanceError(message, code=code)


def _validate_semantic_identifier(value: object, *, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise _malformed("identifier must be non-empty text", code=code)
    return value


def _canonical_json_bytes(value: object) -> bytes:
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return text.encode("utf-8", "strict")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise _malformed("transport JSON value is not serializable scalar Unicode JSON", code="MALFORMED_STREAM_FRAME") from exc


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
            raise UnsupportedFeatureError("unsupported streaming frame version", code="UNSUPPORTED_STREAM_FRAME_VERSION")
        if not isinstance(self.frame_type, str) or not self.frame_type:
            raise _malformed("streaming frame type must be non-empty text", code="MALFORMED_STREAM_FRAME")
        if self.frame_type not in STREAM_FRAME_TYPES:
            raise UnsupportedFeatureError("unsupported streaming frame type", code="UNSUPPORTED_STREAM_FRAME_TYPE")

    def to_abstract(self) -> tuple[Any, ...]:
        self.validate()
        return (self.domain, self.version, self.frame_type, self.payload)

    def to_json(self) -> dict[str, Any]:
        self.validate()
        return {"olpFrame": 1, "type": self.frame_type, "payload": encode_ojve(self.payload)}

    def to_json_seq_bytes(self) -> bytes:
        # RFC 7464 JSON text sequence item: RS + JSON text + LF.
        return b"\x1e" + _canonical_json_bytes(self.to_json()) + b"\n"

    def to_cbor_item(self) -> bytes:
        self.validate()
        try:
            abstract = materialize_map(self.to_abstract())
            return encode_deterministic_cbor(abstract)
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


def process_manifested_stream(
    frames: Iterable[TransportFrameV1],
    *,
    truncated: bool = False,
    understood_critical_extensions: frozenset[str] = frozenset(),
) -> dict[str, object]:
    """Process a parsed manifested bundle stream without assigning semantics to order.

    The first frame must be ``manifest``.  Record/proof/resource ordering after
    that is deliberately ignored.  A caller that detected transport truncation
    sets ``truncated=True``; already present objects still undergo their normal
    identity validation, but stream completeness can never become COMPLETE.
    """

    frames = tuple(frames)
    if len(frames) > STREAM_MAX_FRAMES:
        raise ResourceLimitError("stream frame count exceeds implementation limit")
    if not frames:
        raise _malformed("manifested stream is empty", code="STREAM_MANIFEST_MISSING")
    for frame in frames:
        frame.validate()
    if frames[0].frame_type != "manifest":
        raise _malformed("first manifested-bundle frame must be manifest", code="STREAM_MANIFEST_NOT_FIRST")

    manifest_payload = frames[0].payload
    if not isinstance(manifest_payload, RecordV1):
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
            continue
        if frame.frame_type == "record":
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
                raise _malformed("end frame must be the final semantic frame", code="STREAM_FRAME_AFTER_END")

    if manifest_count != 1:
        raise _malformed("manifested stream must contain exactly one manifest frame", code="DUPLICATE_STREAM_MANIFEST")

    bundle = process_bundle(
        manifest_payload,
        records=records,
        proofs=proofs,
        resources=resources,
        understood_critical_extensions=understood_critical_extensions,
    )

    present_record_ids = sorted(record_identity(item).hex() for item in records)
    present_proof_ids = sorted(proof_identity(item).hex() for item in proofs)
    present_resource_ids = sorted(item.ref.digest.hex() for item in resources)

    complete = not truncated and bundle["closure_status"] == "COMPLETE"
    transport_status = "COMPLETE" if complete else "INCOMPLETE"
    if bundle["status"] == "INVALID":
        transport_status = "INVALID"

    return {
        "transport_status": transport_status,
        "truncated": bool(truncated),
        "end_frame_present": end_seen,
        "result_frame_count": result_frames,
        "bundle": bundle,
        "present_record_identity_hex": present_record_ids,
        "present_proof_identity_hex": present_proof_ids,
        "present_resource_digest_hex": present_resource_ids,
        "present_objects_remain_individually_addressable": True,
        "frame_order_has_evidence_semantics": False,
    }


def negotiate_media_type(accept: Iterable[str], offered: Iterable[str]) -> str | None:
    """Deterministically negotiate already-parsed media ranges.

    The fixture boundary represents the HTTP ``Accept`` field as an ordered
    sequence of media ranges after ordinary HTTP field parsing.  This function
    handles exact ranges plus ``type/*`` and ``*/*`` without inventing an OLP
    media type or overriding explicit caller exclusions.
    """

    accept = tuple(accept)
    offered = tuple(offered)
    for media_range in accept:
        if not isinstance(media_range, str) or ";" in media_range:
            raise _malformed("Accept fixture values must be parsed media ranges without parameters", code="MALFORMED_HTTP_ACCEPT")
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


def validate_content_digest(header_value: str | None, content: bytes, *, required: bool = False) -> dict[str, object]:
    """Validate RFC 9530 Content-Digest ``sha-256`` over HTTP content bytes."""

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
        member = raw_member.strip()
        match = _CONTENT_DIGEST_MEMBER_RE.fullmatch(member)
        if not match:
            raise _malformed("unsupported or malformed Content-Digest dictionary member", code="MALFORMED_CONTENT_DIGEST")
        algorithm = match.group("algorithm")
        if algorithm in members:
            raise _malformed("duplicate Content-Digest algorithm", code="MALFORMED_CONTENT_DIGEST")
        encoded = match.group("value")
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise _malformed("Content-Digest byte sequence is invalid base64", code="MALFORMED_CONTENT_DIGEST") from exc
        # Structured Fields byte sequences have a canonical base64 serialization.
        if base64.b64encode(decoded).decode("ascii") != encoded:
            raise _malformed("Content-Digest byte sequence is not canonical base64", code="MALFORMED_CONTENT_DIGEST")
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
    allowed_authn = {"NOT_REQUIRED", "SUCCEEDED", "MISSING", "FAILED"}
    allowed_authz = {"NOT_APPLICABLE", "ALLOWED", "DENIED"}
    if authentication not in allowed_authn:
        raise _malformed("unknown HTTP authentication state", code="MALFORMED_HTTP_AUTH_STATE")
    if authorization not in allowed_authz:
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
    """Evaluate deterministic server semantics for identity-bearing GET reads."""

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
        return {
            "http_status": 406,
            "reason": "NOT_ACCEPTABLE",
            "global_nonexistence_established": False,
        }

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
            raise _malformed("record/bundle read candidate must be RecordV1 manifest", code="MALFORMED_HTTP_CANDIDATE")
        candidate_digest = record_identity(candidate)
        message_type = "record" if kind == "record" else "bundle"
    else:
        if not isinstance(candidate, OLPProof):
            raise _malformed("proof read candidate must be OLPProof", code="MALFORMED_HTTP_CANDIDATE")
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
    """Evaluate modeled POST operation status without replacing OLP semantics."""

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

    message_type = {
        "resolution": "resolutionResult",
        "disclosure": "disclosureResult",
        "bundleQuery": "bundle",
    }[operation]
    return {
        "http_status": 200,
        "reason": None,
        "message_type": message_type,
        "response_media_type": selected,
        "semantic_status": semantic_status,
        "semantic_status_evaluated": True,
        "http_status_replaces_semantic_status": False,
        "silent_profile_downgrade": False,
    }


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
    """Apply deterministic redirect safety rules without following the redirect."""

    if not is_absolute_uri(original_uri) or not is_absolute_uri(location):
        raise _malformed("redirect URIs must be absolute", code="MALFORMED_HTTP_REDIRECT")
    original = urlsplit(original_uri)
    target = urlsplit(location)
    if original.scheme.lower() == "https" and target.scheme.lower() == "http":
        return {"status": "BLOCKED", "reason": "HTTPS_DOWNGRADE", "forward_credentials": False}
    if method.upper() not in {"GET", "HEAD"} and not allow_sensitive_post_redirect:
        return {"status": "BLOCKED", "reason": "SENSITIVE_METHOD_REDIRECT_BLOCKED", "forward_credentials": False}
    if requested_identity_text is not None:
        if not isinstance(requested_identity_text, str) or not requested_identity_text:
            raise _malformed("requested identity text must be non-empty", code="MALFORMED_HTTP_REDIRECT")
        target_last = target.path.rstrip("/").rsplit("/", 1)[-1]
        if target_last != requested_identity_text:
            return {"status": "BLOCKED", "reason": "REDIRECT_IDENTITY_CHANGED", "forward_credentials": False}

    same_origin = (
        original.scheme.lower(),
        original.hostname,
        original.port or (443 if original.scheme.lower() == "https" else 80),
    ) == (
        target.scheme.lower(),
        target.hostname,
        target.port or (443 if target.scheme.lower() == "https" else 80),
    )
    forward_credentials = bool(credentials_present and (same_origin or allow_cross_origin_credentials))
    return {
        "status": "ALLOWED",
        "reason": None,
        "same_origin": same_origin,
        "forward_credentials": forward_credentials,
    }


def separate_http_auth_from_olp(
    *,
    http_authentication: str,
    service_authorization: str,
    olp_cryptographic_validity: str,
    olp_authority_evidence: str = "NOT_EVALUATED",
) -> dict[str, object]:
    """Return authentication/authorization/proof dimensions without conflation."""

    _authorization_gate(http_authentication, service_authorization)
    _validate_semantic_identifier(olp_cryptographic_validity, code="MALFORMED_OLP_STATUS")
    _validate_semantic_identifier(olp_authority_evidence, code="MALFORMED_OLP_STATUS")
    return {
        "http_authentication": http_authentication,
        "service_authorization": service_authorization,
        "olp_cryptographic_validity": olp_cryptographic_validity,
        "olp_authority_evidence": olp_authority_evidence,
        "http_authentication_changes_olp_validity": False,
        "olp_proof_grants_http_authorization": False,
    }
