"""Deterministic redirect policy for the Milestone 24 HTTP semantic model."""

from __future__ import annotations

from urllib.parse import SplitResult, urlsplit

from .errors import ConformanceError
from .values import is_absolute_uri


def _malformed(message: str) -> ConformanceError:
    return ConformanceError(message, code="MALFORMED_HTTP_REDIRECT")


def _parse_http_uri(value: str) -> tuple[SplitResult, tuple[str, str, int]]:
    if not is_absolute_uri(value):
        raise _malformed("redirect URI must be absolute")
    try:
        parts = urlsplit(value)
        scheme = parts.scheme.lower()
        if scheme not in {"http", "https"}:
            raise _malformed("redirect URI must use HTTP or HTTPS")
        if parts.username is not None or parts.password is not None:
            raise _malformed("redirect URI userinfo is not accepted by the M24 policy model")
        if parts.hostname is None:
            raise _malformed("redirect URI must contain a host")
        port = parts.port or (443 if scheme == "https" else 80)
    except ValueError as exc:
        raise _malformed("redirect URI could not be parsed safely") from exc
    return parts, (scheme, parts.hostname.lower(), port)


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
    """Apply redirect safety rules without performing or following a request."""

    original, original_origin = _parse_http_uri(original_uri)
    target, target_origin = _parse_http_uri(location)

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
            raise _malformed("requested identity text must be non-empty")
        target_last = target.path.rstrip("/").rsplit("/", 1)[-1]
        if target_last != requested_identity_text:
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
