"""Deterministic, offline-first executable core for Specification 0009.

The executable resolver intentionally consumes caller-supplied resolver snapshots. It never
performs network I/O itself. This keeps conformance deterministic while preserving the
security semantics a real network resolver must enforce before dereferencing attacker-
controlled identifiers.
"""
from __future__ import annotations

import hashlib
import ipaddress
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from .encoding.proof_identity import proof_identity
from .encoding.record_identity import record_identity
from .errors import ConformanceError, ResourceLimitError
from .model.bundle import ResourceRefV1
from .model.evidence import EvidenceKind, EvidenceRefV1
from .model.proof import OLPProof
from .model.record import RecordV1
from .model.resolution import ResolutionRequestV1
from .values import is_absolute_uri


@dataclass(frozen=True, slots=True)
class ResolutionLimits:
    max_sources: int = 64
    max_candidates: int = 10_000
    max_chain: int = 32


def _ref_json(ref: EvidenceRefV1) -> dict[str, object]:
    return {"kind": int(ref.kind), "identity_digest_hex": ref.identity_digest.hex()}


def _base(
    status: str,
    *,
    errors: Iterable[str] = (),
    redirects: Iterable[str] = (),
    network_requests: int = 0,
    freshness: str = "NOT_APPLICABLE",
) -> dict[str, object]:
    return {
        "status": status,
        "matches": [],
        "provenance": [],
        "freshness": freshness,
        "conflicts": [],
        "redirects": list(redirects),
        "warnings": [],
        "errors": list(errors),
        "network_requests": network_requests,
    }


def _blocked_network_target(uri: str) -> bool:
    parsed = urlsplit(uri)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return True
    lowered = host.lower()
    if lowered == "localhost" or lowered.endswith(".localhost"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return bool(
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _source_freshness(source: Mapping[str, Any]) -> str:
    value = source.get("freshness", "NOT_APPLICABLE")
    if not isinstance(value, str):
        raise ConformanceError("resolver freshness MUST be text", code="RESOLVER_RESPONSE_MALFORMED")
    return value


def _freshness_allows(request: ResolutionRequestV1, source: Mapping[str, Any]) -> bool:
    return not request.require_fresh or _source_freshness(source) == "FRESH"


def _size_exceeds(request: ResolutionRequestV1, size: int) -> bool:
    return request.max_bytes is not None and size > request.max_bytes


def resolve_request(
    request: ResolutionRequestV1,
    *,
    sources: Iterable[Mapping[str, Any]] = (),
    limits: ResolutionLimits = ResolutionLimits(),
) -> dict[str, object]:
    request.validate()
    sources = tuple(sources)
    if len(sources) > limits.max_sources:
        raise ResourceLimitError("resolution source count exceeds implementation limit")

    if request.target_class == "evidence":
        return _resolve_evidence(request, sources, limits)
    if request.target_class == "externalResource":
        return _resolve_external_resource(request, sources, limits)
    raise ConformanceError("unsupported executable target class", code="UNSUPPORTED_TARGET_CLASS")


def _resolve_evidence(
    request: ResolutionRequestV1,
    sources: tuple[Mapping[str, Any], ...],
    limits: ResolutionLimits,
) -> dict[str, object]:
    target = EvidenceRefV1.from_value(request.target)
    candidates_seen = 0
    mismatches: list[dict[str, object]] = []
    freshness_blocked = False

    for source_index, source in enumerate(sources):
        source_class = source.get("source_class")
        source_id = source.get("source_identifier")
        if source_class not in {"bundle", "localStore"}:
            continue
        candidates = source.get("candidates", ())
        if not isinstance(candidates, (tuple, list)):
            raise ConformanceError("resolver candidates MUST be array", code="RESOLVER_RESPONSE_MALFORMED")

        for candidate in candidates:
            candidates_seen += 1
            if candidates_seen > limits.max_candidates:
                return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LIMIT_EXCEEDED"])
            if not isinstance(candidate, Mapping):
                raise ConformanceError("resolver candidate MUST be map", code="RESOLVER_RESPONSE_MALFORMED")
            lookup = EvidenceRefV1.from_value(candidate["lookup_ref"])
            if lookup != target:
                continue

            declared_size = candidate.get("size_bytes")
            if declared_size is not None:
                if isinstance(declared_size, bool) or not isinstance(declared_size, int) or declared_size < 0:
                    raise ConformanceError("candidate size_bytes malformed", code="RESOLVER_RESPONSE_MALFORMED")
                if _size_exceeds(request, declared_size):
                    return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LIMIT_EXCEEDED"])

            actual_ref: EvidenceRefV1
            if target.kind is EvidenceKind.RECORD:
                record = candidate.get("record")
                if not isinstance(record, RecordV1):
                    raise ConformanceError("candidate record is malformed", code="RESOLVER_RESPONSE_MALFORMED")
                actual_ref = EvidenceRefV1(EvidenceKind.RECORD, record_identity(record))
            else:
                proof = candidate.get("proof")
                if not isinstance(proof, OLPProof):
                    raise ConformanceError("candidate proof is malformed", code="RESOLVER_RESPONSE_MALFORMED")
                actual_ref = EvidenceRefV1(EvidenceKind.PROOF, proof_identity(proof))

            if actual_ref != target:
                mismatches.append(
                    {
                        "requested": _ref_json(target),
                        "actual": _ref_json(actual_ref),
                        "source_index": source_index,
                    }
                )
                continue

            if not _freshness_allows(request, source):
                freshness_blocked = True
                continue

            result = _base("RESOLVED", freshness=_source_freshness(source))
            result["matches"] = [
                {
                    "ref": _ref_json(target),
                    "source_class": source_class,
                    "source_identifier": source_id,
                }
            ]
            result["provenance"] = [
                {
                    "source_class": source_class,
                    "source_identifier": source_id,
                    "source_index": source_index,
                }
            ]
            result["conflicts"] = mismatches
            return result

    if freshness_blocked:
        result = _base("POLICY_BLOCKED", errors=["FRESHNESS_REQUIREMENT_NOT_MET"])
        result["conflicts"] = mismatches
        return result
    if mismatches:
        result = _base("IDENTITY_MISMATCH", errors=["RESOLVED_IDENTITY_MISMATCH"])
        result["conflicts"] = mismatches
        return result
    return _base("NOT_FOUND", errors=["RESOLUTION_NOT_FOUND"])


def _resolve_external_resource(
    request: ResolutionRequestV1,
    sources: tuple[Mapping[str, Any], ...],
    limits: ResolutionLimits,
) -> dict[str, object]:
    target = request.target
    target_uri: str | None
    target_ref: ResourceRefV1 | None
    if isinstance(target, str):
        target_uri, target_ref = target, None
    else:
        target_ref = ResourceRefV1.from_value(target)
        target_uri = target_ref.resource_id

    freshness_blocked = False

    # Package/local source hits are always attempted before network policy.
    for source_index, source in enumerate(sources):
        if source.get("source_class") not in {"bundle", "localStore"}:
            continue
        resources = source.get("resources", ())
        if not isinstance(resources, (tuple, list)):
            raise ConformanceError("resource candidates MUST be array", code="RESOLVER_RESPONSE_MALFORMED")
        for resource in resources:
            if not isinstance(resource, Mapping):
                raise ConformanceError("resource candidate malformed", code="RESOLVER_RESPONSE_MALFORMED")
            ref = resource.get("ref")
            content = resource.get("content")
            if not isinstance(ref, ResourceRefV1) or not isinstance(content, bytes):
                raise ConformanceError("resource candidate malformed", code="RESOLVER_RESPONSE_MALFORMED")
            if target_ref is not None and ref.canonical_bytes() != target_ref.canonical_bytes():
                continue
            if target_ref is None and ref.resource_id != target_uri:
                continue
            if request.accept and ref.media_type not in request.accept:
                continue
            if _size_exceeds(request, len(content)):
                return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LIMIT_EXCEEDED"])
            if ref.hash_algorithm == -16 and hashlib.sha256(content).digest() != ref.digest:
                result = _base("IDENTITY_MISMATCH", errors=["RESOURCE_DIGEST_MISMATCH"])
                result["conflicts"] = [{"resource_id": ref.resource_id, "source_index": source_index}]
                return result
            if not _freshness_allows(request, source):
                freshness_blocked = True
                continue
            result = _base("RESOLVED", freshness=_source_freshness(source))
            result["matches"] = [
                {
                    "resource_id": ref.resource_id,
                    "digest_hex": ref.digest.hex(),
                    "source_class": source.get("source_class"),
                    "source_identifier": source.get("source_identifier"),
                }
            ]
            result["provenance"] = [
                {
                    "source_class": source.get("source_class"),
                    "source_identifier": source.get("source_identifier"),
                    "source_index": source_index,
                }
            ]
            return result

    if freshness_blocked:
        return _base("POLICY_BLOCKED", errors=["FRESHNESS_REQUIREMENT_NOT_MET"])

    network_sources = [(i, s) for i, s in enumerate(sources) if s.get("source_class") == "network"]
    if request.offline_only or not network_sources:
        return _base("POLICY_BLOCKED", errors=["NETWORK_ACCESS_DISABLED"])
    if target_uri is None or not is_absolute_uri(target_uri):
        return _base("UNSUPPORTED", errors=["UNSUPPORTED_IDENTIFIER_SCHEME"])
    parsed = urlsplit(target_uri)
    if parsed.scheme not in {"http", "https"}:
        return _base("UNSUPPORTED", errors=["UNSUPPORTED_IDENTIFIER_SCHEME"])
    if _blocked_network_target(target_uri):
        return _base("POLICY_BLOCKED", errors=["RESOLUTION_POLICY_BLOCKED"])

    # The executable core models deterministic network snapshots; it does not perform I/O.
    for source_index, source in network_sources:
        chain = source.get("chain", ())
        if not isinstance(chain, (tuple, list)):
            raise ConformanceError("network chain MUST be array", code="RESOLVER_RESPONSE_MALFORMED")
        if len(chain) > limits.max_chain:
            return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LIMIT_EXCEEDED"])
        seen: set[str] = set()
        for item in chain:
            if not isinstance(item, str) or not is_absolute_uri(item):
                raise ConformanceError("network chain identifier malformed", code="RESOLVER_RESPONSE_MALFORMED")
            if item in seen:
                return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LOOP"], redirects=chain)
            seen.add(item)
            if _blocked_network_target(item):
                return _base("POLICY_BLOCKED", errors=["RESOLUTION_POLICY_BLOCKED"], redirects=chain)

        redirects = tuple(source.get("redirects", ()))
        if any(not isinstance(item, str) or not is_absolute_uri(item) for item in redirects):
            raise ConformanceError("redirect identifier malformed", code="RESOLVER_RESPONSE_MALFORMED")
        if redirects and not request.allow_redirects:
            return _base("POLICY_BLOCKED", errors=["REDIRECT_BLOCKED"], redirects=redirects)
        if any(_blocked_network_target(item) for item in redirects):
            return _base("POLICY_BLOCKED", errors=["RESOLUTION_POLICY_BLOCKED"], redirects=redirects)

        response_bytes = source.get("response_bytes")
        if response_bytes is not None:
            if isinstance(response_bytes, bool) or not isinstance(response_bytes, int) or response_bytes < 0:
                raise ConformanceError("response_bytes malformed", code="RESOLVER_RESPONSE_MALFORMED")
            if _size_exceeds(request, response_bytes):
                return _base("LIMIT_EXCEEDED", errors=["RESOLUTION_LIMIT_EXCEEDED"], redirects=redirects)

        freshness = _source_freshness(source)
        if request.require_fresh and freshness != "FRESH":
            return _base(
                "POLICY_BLOCKED",
                errors=["FRESHNESS_REQUIREMENT_NOT_MET"],
                redirects=redirects,
                network_requests=1,
                freshness=freshness,
            )

        # Snapshot response. Count one logical network request only after all preflight policy checks pass.
        if source.get("status") == "notFound":
            return _base(
                "NOT_FOUND",
                errors=["RESOLUTION_NOT_FOUND"],
                redirects=redirects,
                network_requests=1,
                freshness=freshness,
            )
        if source.get("status") == "unavailable":
            return _base(
                "UNAVAILABLE",
                errors=["RESOLUTION_UNAVAILABLE"],
                redirects=redirects,
                network_requests=1,
                freshness=freshness,
            )
        if source.get("status") == "resolved":
            result = _base("RESOLVED", redirects=redirects, network_requests=1, freshness=freshness)
            result["matches"] = [
                {
                    "resource_id": source.get("resolved_id", target_uri),
                    "source_class": "network",
                    "source_identifier": source.get("source_identifier"),
                }
            ]
            result["provenance"] = [
                {
                    "source_class": "network",
                    "source_identifier": source.get("source_identifier"),
                    "source_index": source_index,
                }
            ]
            return result
        raise ConformanceError("unknown network snapshot status", code="RESOLVER_RESPONSE_MALFORMED")
    return _base("NOT_FOUND", errors=["RESOLUTION_NOT_FOUND"])
