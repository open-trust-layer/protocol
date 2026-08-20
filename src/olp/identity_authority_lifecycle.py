"""Executable core for Specifications 0006 and 0007.

This module validates immutable identity/authority/lifecycle statement profiles and
performs only deterministic, policy-separated evaluations.  It deliberately does
not produce a protocol-global identity merge, current status, trust score, or
``authorized`` boolean.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import ConformanceError, UnsupportedFeatureError
from .model.proof import is_rfc3339, parse_rfc3339
from .values import is_absolute_uri, validate_record_value

PRINCIPAL_RELATION_DOMAIN = "OLP-PRINCIPAL-RELATION"
AUTHORITY_GRANT_DOMAIN = "OLP-AUTHORITY-GRANT"
AUTHORITY_STATUS_DOMAIN = "OLP-AUTHORITY-STATUS"
LIFECYCLE_STATUS_DOMAIN = "OLP-LIFECYCLE-STATUS"

CORE_PRINCIPAL_RELATIONS = frozenset(
    {"controlsVerificationMethod", "sameSubjectAs", "memberOf", "holdsRole"}
)
CORE_AUTHORITY_STATUS_EVENTS = frozenset({"suspend", "resume", "revoke"})
CORE_LIFECYCLE_EVENTS = frozenset(
    {"activate", "suspend", "resume", "retire", "revoke", "compromise", "deprecate"}
)
CORE_LIFECYCLE_TARGETS = frozenset({"record", "proof", "verificationMethod", "principal"})


def _malformed(message: str, code: str) -> ConformanceError:
    return ConformanceError(message, code=code)


def _array(value: Any, size: int, code: str, label: str) -> tuple[Any, ...]:
    if not isinstance(value, (tuple, list)) or len(value) != size:
        raise _malformed(f"{label} MUST be a {size}-element array", code)
    return tuple(value)


def _uri(value: Any, code: str, label: str) -> str:
    if not is_absolute_uri(value):
        raise _malformed(f"{label} MUST be an absolute URI", code)
    return value


def _nullable_uri(value: Any, code: str, label: str) -> str | None:
    return None if value is None else _uri(value, code, label)


def _time(value: Any, code: str, label: str) -> str | None:
    if value is None:
        return None
    if not is_rfc3339(value):
        raise _malformed(f"{label} MUST be RFC 3339 or null", code)
    return value


def _uri_map(value: Any, code: str, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise _malformed(f"{label} MUST be a map", code)
    result: dict[str, Any] = {}
    for key, item in value.items():
        if not is_absolute_uri(key):
            raise _malformed(f"{label} keys MUST be absolute URIs", code)
        validate_record_value(item, path=f"{label}[{key!r}]")
        result[key] = item
    return result


def _critical(
    value: Any,
    qualifiers: Mapping[str, Any],
    *,
    code: str,
    unsupported_code: str,
    understood: frozenset[str],
) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        raise _malformed("critical qualifiers MUST be an array", code)
    items = tuple(value)
    if any(not isinstance(item, str) for item in items) or len(items) != len(set(items)):
        raise _malformed("critical qualifiers MUST contain unique text identifiers", code)
    if items != tuple(sorted(items, key=lambda item: item.encode("utf-8"))):
        raise _malformed("critical qualifiers MUST be canonically sorted", code)
    for item in items:
        if not is_absolute_uri(item) or item not in qualifiers:
            raise _malformed("critical qualifier MUST name a present URI qualifier", code)
    if set(items) - set(understood):
        raise UnsupportedFeatureError("unsupported critical qualifier", code=unsupported_code)
    return items


def _evidence_ref(value: Any, *, required_kind: int | None = None, code: str) -> tuple[int, bytes]:
    raw = _array(value, 2, code, "EvidenceRefV1")
    kind, digest = raw
    if isinstance(kind, bool) or not isinstance(kind, int) or kind not in (0, 1):
        raise _malformed("EvidenceRefV1 kind MUST be 0 or 1", code)
    if required_kind is not None and kind != required_kind:
        raise _malformed("EvidenceRefV1 kind does not match target category", code)
    if not isinstance(digest, bytes) or len(digest) != 32:
        raise _malformed("EvidenceRefV1 digest MUST contain exactly 32 octets", code)
    return kind, digest


def _ref_json(value: tuple[int, bytes] | None) -> list[Any] | None:
    if value is None:
        return None
    return [value[0], value[1].hex()]


def _principal_object(value: Any) -> tuple[int, str]:
    kind, identifier = _array(value, 2, "MALFORMED_PRINCIPAL_RELATION", "PrincipalObjectRefV1")
    if isinstance(kind, bool) or not isinstance(kind, int):
        raise _malformed("principal object kind MUST be an integer", "MALFORMED_PRINCIPAL_RELATION")
    if kind not in (0, 1, 2):
        raise UnsupportedFeatureError(
            "unsupported principal object kind", code="UNSUPPORTED_PRINCIPAL_OBJECT_KIND"
        )
    return kind, _uri(identifier, "MALFORMED_PRINCIPAL_RELATION", "principal object identifier")


def _principal_relation(
    value: Any, *, understood_critical: frozenset[str] = frozenset()
) -> dict[str, Any]:
    raw = _array(value, 8, "MALFORMED_PRINCIPAL_RELATION", "PrincipalRelationStatementV1")
    domain, version, relation_type, subject, object_raw, context, qualifiers_raw, critical_raw = raw
    if domain != PRINCIPAL_RELATION_DOMAIN:
        raise _malformed("invalid principal relation discriminator", "MALFORMED_PRINCIPAL_RELATION")
    if isinstance(version, bool) or not isinstance(version, int):
        raise _malformed("principal relation version MUST be integer", "MALFORMED_PRINCIPAL_RELATION")
    if version != 1:
        raise UnsupportedFeatureError(
            "unsupported principal relation version", code="UNSUPPORTED_PRINCIPAL_RELATION_VERSION"
        )
    if not isinstance(relation_type, str) or not relation_type:
        raise _malformed("relation type MUST be non-empty text", "MALFORMED_PRINCIPAL_RELATION")
    if relation_type not in CORE_PRINCIPAL_RELATIONS:
        if not is_absolute_uri(relation_type):
            raise _malformed("unknown compact principal relation", "MALFORMED_PRINCIPAL_RELATION")
        raise UnsupportedFeatureError(
            "unsupported principal relation type", code="UNSUPPORTED_PRINCIPAL_RELATION_TYPE"
        )
    subject = _uri(subject, "MALFORMED_PRINCIPAL_RELATION", "principal relation subject")
    object_kind, object_id = _principal_object(object_raw)
    context = _nullable_uri(context, "MALFORMED_PRINCIPAL_RELATION", "principal relation context")
    qualifiers = _uri_map(qualifiers_raw, "MALFORMED_PRINCIPAL_RELATION", "principal relation qualifiers")
    critical = _critical(
        critical_raw,
        qualifiers,
        code="MALFORMED_PRINCIPAL_RELATION",
        unsupported_code="UNSUPPORTED_CRITICAL_PRINCIPAL_QUALIFIER",
        understood=understood_critical,
    )

    expected_kind = {
        "controlsVerificationMethod": 1,
        "sameSubjectAs": 0,
        "memberOf": 0,
        "holdsRole": 2,
    }[relation_type]
    if object_kind != expected_kind:
        raise _malformed("principal relation object kind is invalid for relation type", "INVALID_PRINCIPAL_RELATION_OBJECT")
    if relation_type == "holdsRole":
        if context is None:
            raise _malformed("holdsRole requires context", "INVALID_PRINCIPAL_RELATION_CONTEXT")
    elif context is not None:
        raise _malformed("core principal relation forbids context", "INVALID_PRINCIPAL_RELATION_CONTEXT")

    return {
        "relation_type": relation_type,
        "subject": subject,
        "object_kind": object_kind,
        "object_identifier": object_id,
        "context": context,
        "critical": list(critical),
        "uninterpreted_qualifiers": sorted(
            set(qualifiers) - set(understood_critical), key=lambda item: item.encode("utf-8")
        ),
        "trust": "NOT_EVALUATED",
        "authority": "NOT_EVALUATED",
    }


def _authority_resource(value: Any) -> tuple[int, Any] | None:
    if value is None:
        return None
    kind, item = _array(value, 2, "MALFORMED_AUTHORITY_GRANT", "AuthorityResourceRefV1")
    if isinstance(kind, bool) or not isinstance(kind, int):
        raise _malformed("authority resource kind MUST be integer", "MALFORMED_AUTHORITY_GRANT")
    if kind == 0:
        return 0, _uri(item, "MALFORMED_AUTHORITY_GRANT", "authority resource URI")
    if kind == 1:
        return 1, _evidence_ref(item, code="MALFORMED_AUTHORITY_GRANT")
    raise UnsupportedFeatureError(
        "unsupported authority resource kind", code="UNSUPPORTED_AUTHORITY_RESOURCE_KIND"
    )


def _resource_json(value: tuple[int, Any] | None) -> Any:
    if value is None:
        return None
    if value[0] == 0:
        return [0, value[1]]
    return [1, _ref_json(value[1])]


def _authority_grant(
    value: Any, *, understood_constraints: frozenset[str] = frozenset()
) -> dict[str, Any]:
    raw = _array(value, 13, "MALFORMED_AUTHORITY_GRANT", "AuthorityGrantStatementV1")
    (
        domain,
        version,
        grantor,
        grantee,
        action,
        resource_raw,
        context,
        valid_from,
        valid_until,
        delegable,
        parent_raw,
        constraints_raw,
        extensions_raw,
    ) = raw
    if domain != AUTHORITY_GRANT_DOMAIN:
        raise _malformed("invalid authority grant discriminator", "MALFORMED_AUTHORITY_GRANT")
    if isinstance(version, bool) or not isinstance(version, int):
        raise _malformed("authority grant version MUST be integer", "MALFORMED_AUTHORITY_GRANT")
    if version != 1:
        raise UnsupportedFeatureError(
            "unsupported authority grant version", code="UNSUPPORTED_AUTHORITY_GRANT_VERSION"
        )
    grantor = _uri(grantor, "MALFORMED_AUTHORITY_GRANT", "grantor")
    grantee = _uri(grantee, "MALFORMED_AUTHORITY_GRANT", "grantee")
    action = _uri(action, "MALFORMED_AUTHORITY_GRANT", "action")
    resource = _authority_resource(resource_raw)
    context = _nullable_uri(context, "MALFORMED_AUTHORITY_GRANT", "authority context")
    valid_from = _time(valid_from, "MALFORMED_AUTHORITY_GRANT", "validFrom")
    valid_until = _time(valid_until, "MALFORMED_AUTHORITY_GRANT", "validUntil")
    if valid_from is not None and valid_until is not None and parse_rfc3339(valid_from) >= parse_rfc3339(valid_until):
        raise _malformed("validFrom MUST be earlier than validUntil", "INVALID_AUTHORITY_INTERVAL")
    if not isinstance(delegable, bool):
        raise _malformed("delegable MUST be boolean", "MALFORMED_AUTHORITY_GRANT")
    parent = None if parent_raw is None else _evidence_ref(
        parent_raw, required_kind=0, code="MALFORMED_AUTHORITY_GRANT"
    )
    constraints = _uri_map(constraints_raw, "MALFORMED_AUTHORITY_GRANT", "authority constraints")
    unknown = set(constraints) - set(understood_constraints)
    if unknown:
        raise UnsupportedFeatureError("unsupported authority constraint", code="UNSUPPORTED_AUTHORITY_CONSTRAINT")
    extensions = _uri_map(extensions_raw, "MALFORMED_AUTHORITY_GRANT", "authority extensions")
    return {
        "grantor": grantor,
        "grantee": grantee,
        "action": action,
        "resource": resource,
        "context": context,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "delegable": delegable,
        "parent_grant": parent,
        "constraints": constraints,
        "extensions": extensions,
    }


def _interval(grant: Mapping[str, Any], evaluation_time: str | None) -> str:
    if evaluation_time is None:
        return "NOT_EVALUATED"
    if not is_rfc3339(evaluation_time):
        raise _malformed("evaluation_time MUST be RFC 3339", "MALFORMED_EVALUATION_CONTEXT")
    now = parse_rfc3339(evaluation_time)
    lower = parse_rfc3339(grant["valid_from"]) if grant["valid_from"] is not None else None
    upper = parse_rfc3339(grant["valid_until"]) if grant["valid_until"] is not None else None
    if lower is None and upper is None:
        return "NO_DECLARED_BOUND"
    if lower is not None and now < lower:
        return "BEFORE_DECLARED_INTERVAL"
    if upper is not None and now >= upper:
        return "AFTER_DECLARED_INTERVAL"
    return "WITHIN_DECLARED_INTERVAL"


def _grant_output(grant: Mapping[str, Any], evaluation_time: str | None) -> dict[str, Any]:
    return {
        "grantor": grant["grantor"],
        "grantee": grant["grantee"],
        "action": grant["action"],
        "resource": _resource_json(grant["resource"]),
        "context": grant["context"],
        "delegable": grant["delegable"],
        "parent_grant": _ref_json(grant["parent_grant"]),
        "temporal_applicability": _interval(grant, evaluation_time),
        "grant_attribution": "NOT_EVALUATED",
        "status": "NOT_EVALUATED",
        "policy_decision": "NOT_EVALUATED",
    }


def _ref_equal(left: tuple[int, bytes] | None, right: tuple[int, bytes] | None) -> bool:
    return left == right


def _resource_equal(left: tuple[int, Any] | None, right: tuple[int, Any] | None) -> bool:
    return left == right


def _interval_within(parent: Mapping[str, Any], child: Mapping[str, Any]) -> bool:
    p_from = parse_rfc3339(parent["valid_from"]) if parent["valid_from"] is not None else None
    p_until = parse_rfc3339(parent["valid_until"]) if parent["valid_until"] is not None else None
    c_from = parse_rfc3339(child["valid_from"]) if child["valid_from"] is not None else None
    c_until = parse_rfc3339(child["valid_until"]) if child["valid_until"] is not None else None
    if p_from is not None and (c_from is None or c_from < p_from):
        return False
    if p_until is not None and (c_until is None or c_until > p_until):
        return False
    return True


def _delegation(payload: Mapping[str, Any]) -> dict[str, Any]:
    understood = frozenset(payload.get("understood_constraints", ()))
    child = _authority_grant(payload["child"], understood_constraints=understood)
    if child["parent_grant"] is None:
        return {
            "delegation_status": "NO_PARENT_CLAIMED",
            "reasons": [],
            "scope": "NOT_EVALUATED",
            "policy_decision": "NOT_EVALUATED",
        }
    if "parent" not in payload or "parent_reference" not in payload:
        return {
            "delegation_status": "UNRESOLVED_PARENT",
            "reasons": ["PARENT_GRANT_UNRESOLVED"],
            "scope": "INDETERMINATE",
            "policy_decision": "NOT_EVALUATED",
        }
    supplied_ref = _evidence_ref(payload["parent_reference"], required_kind=0, code="MALFORMED_DELEGATION_INPUT")
    if not _ref_equal(child["parent_grant"], supplied_ref):
        return {
            "delegation_status": "UNRESOLVED_PARENT",
            "reasons": ["PARENT_GRANT_REFERENCE_MISMATCH"],
            "scope": "INDETERMINATE",
            "policy_decision": "NOT_EVALUATED",
        }
    parent = _authority_grant(payload["parent"], understood_constraints=understood)
    reasons: list[str] = []
    if parent["grantee"] != child["grantor"]:
        reasons.append("DELEGATION_PRINCIPAL_MISMATCH")
    if not parent["delegable"]:
        reasons.append("PARENT_GRANT_NOT_DELEGABLE")

    exact_scope = True
    if parent["action"] != child["action"]:
        reasons.append("DELEGATION_ACTION_SCOPE_MISMATCH")
        exact_scope = False
    if not _resource_equal(parent["resource"], child["resource"]):
        reasons.append("DELEGATION_RESOURCE_SCOPE_MISMATCH")
        exact_scope = False
    if parent["context"] != child["context"]:
        reasons.append("DELEGATION_CONTEXT_SCOPE_MISMATCH")
        exact_scope = False
    if not _interval_within(parent, child):
        reasons.append("DELEGATION_TIME_SCOPE_MISMATCH")
        exact_scope = False
    if parent["constraints"] != child["constraints"]:
        reasons.append("DELEGATION_CONSTRAINT_SCOPE_INDETERMINATE")
        exact_scope = False

    if reasons:
        status = "NOT_SUPPORTED"
        scope = "WITHIN_PARENT_EXACT_BASELINE" if exact_scope else "OUTSIDE_OR_INDETERMINATE"
    else:
        status = "SUPPORTED"
        scope = "WITHIN_PARENT_EXACT_BASELINE"
    return {
        "delegation_status": status,
        "reasons": reasons,
        "scope": scope,
        "parent_reference": _ref_json(supplied_ref),
        "policy_decision": "NOT_EVALUATED",
    }


def _authority_status(
    value: Any, *, understood_critical: frozenset[str] = frozenset()
) -> dict[str, Any]:
    raw = _array(value, 8, "MALFORMED_AUTHORITY_STATUS", "AuthorityStatusStatementV1")
    domain, version, target_raw, event, effective_at, reason, qualifiers_raw, critical_raw = raw
    if domain != AUTHORITY_STATUS_DOMAIN:
        raise _malformed("invalid authority status discriminator", "MALFORMED_AUTHORITY_STATUS")
    if isinstance(version, bool) or not isinstance(version, int):
        raise _malformed("authority status version MUST be integer", "MALFORMED_AUTHORITY_STATUS")
    if version != 1:
        raise UnsupportedFeatureError("unsupported authority status version", code="UNSUPPORTED_AUTHORITY_STATUS_VERSION")
    target = _evidence_ref(target_raw, required_kind=0, code="MALFORMED_AUTHORITY_STATUS")
    if not isinstance(event, str) or not event:
        raise _malformed("authority status event MUST be text", "MALFORMED_AUTHORITY_STATUS")
    if event not in CORE_AUTHORITY_STATUS_EVENTS:
        if not is_absolute_uri(event):
            raise _malformed("unknown compact authority status event", "MALFORMED_AUTHORITY_STATUS")
        raise UnsupportedFeatureError("unsupported authority status event", code="UNSUPPORTED_AUTHORITY_STATUS_EVENT")
    effective_at = _time(effective_at, "MALFORMED_AUTHORITY_STATUS", "effectiveAt")
    reason = _nullable_uri(reason, "MALFORMED_AUTHORITY_STATUS", "authority status reason")
    qualifiers = _uri_map(qualifiers_raw, "MALFORMED_AUTHORITY_STATUS", "authority status qualifiers")
    critical = _critical(
        critical_raw,
        qualifiers,
        code="MALFORMED_AUTHORITY_STATUS",
        unsupported_code="UNSUPPORTED_CRITICAL_AUTHORITY_STATUS_QUALIFIER",
        understood=understood_critical,
    )
    return {
        "target_grant": _ref_json(target),
        "event": event,
        "effective_at": effective_at,
        "reason": reason,
        "critical": list(critical),
        "producer_authority": "NOT_EVALUATED",
        "mutates_target": False,
    }


def _lifecycle_target(value: Any) -> tuple[str, Any]:
    target_type, reference = _array(value, 2, "MALFORMED_LIFECYCLE_TARGET", "LifecycleTargetV1")
    if not isinstance(target_type, str) or not target_type:
        raise _malformed("lifecycle target type MUST be text", "MALFORMED_LIFECYCLE_TARGET")
    if target_type not in CORE_LIFECYCLE_TARGETS:
        if not is_absolute_uri(target_type):
            raise _malformed("unknown compact lifecycle target type", "MALFORMED_LIFECYCLE_TARGET")
        raise UnsupportedFeatureError("unsupported lifecycle target type", code="UNSUPPORTED_LIFECYCLE_TARGET_TYPE")
    if target_type == "record":
        return target_type, _evidence_ref(reference, required_kind=0, code="MALFORMED_LIFECYCLE_TARGET")
    if target_type == "proof":
        return target_type, _evidence_ref(reference, required_kind=1, code="MALFORMED_LIFECYCLE_TARGET")
    return target_type, _uri(reference, "MALFORMED_LIFECYCLE_TARGET", "lifecycle target identifier")


def _target_json(target: tuple[str, Any]) -> list[Any]:
    if target[0] in {"record", "proof"}:
        return [target[0], _ref_json(target[1])]
    return [target[0], target[1]]


def _lifecycle_status(
    value: Any, *, understood_critical: frozenset[str] = frozenset()
) -> dict[str, Any]:
    raw = _array(value, 12, "MALFORMED_LIFECYCLE_STATUS", "LifecycleStatusStatementV1")
    (
        domain,
        version,
        target_raw,
        event,
        status_authority,
        effective_at,
        sequence,
        scope,
        next_update,
        reason,
        qualifiers_raw,
        critical_raw,
    ) = raw
    if domain != LIFECYCLE_STATUS_DOMAIN:
        raise _malformed("invalid lifecycle status discriminator", "MALFORMED_LIFECYCLE_STATUS")
    if isinstance(version, bool) or not isinstance(version, int):
        raise _malformed("lifecycle status version MUST be integer", "MALFORMED_LIFECYCLE_STATUS")
    if version != 1:
        raise UnsupportedFeatureError("unsupported lifecycle status version", code="UNSUPPORTED_LIFECYCLE_STATUS_VERSION")
    target = _lifecycle_target(target_raw)
    if not isinstance(event, str) or not event:
        raise _malformed("lifecycle event MUST be text", "MALFORMED_LIFECYCLE_STATUS")
    if event not in CORE_LIFECYCLE_EVENTS:
        if not is_absolute_uri(event):
            raise _malformed("unknown compact lifecycle event", "MALFORMED_LIFECYCLE_STATUS")
        raise UnsupportedFeatureError("unsupported lifecycle event", code="UNSUPPORTED_LIFECYCLE_EVENT")
    status_authority = _nullable_uri(status_authority, "MALFORMED_LIFECYCLE_STATUS", "statusAuthority")
    effective_at = _time(effective_at, "MALFORMED_LIFECYCLE_STATUS", "effectiveAt")
    if sequence is not None:
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise _malformed("sequence MUST be a non-negative integer or null", "MALFORMED_LIFECYCLE_STATUS")
        if status_authority is None:
            raise _malformed("sequence requires statusAuthority", "MALFORMED_LIFECYCLE_STATUS")
    scope = _nullable_uri(scope, "MALFORMED_LIFECYCLE_STATUS", "scope")
    next_update = _time(next_update, "MALFORMED_LIFECYCLE_STATUS", "nextUpdate")
    reason = _nullable_uri(reason, "MALFORMED_LIFECYCLE_STATUS", "reason")
    qualifiers = _uri_map(qualifiers_raw, "MALFORMED_LIFECYCLE_STATUS", "lifecycle qualifiers")
    critical = _critical(
        critical_raw,
        qualifiers,
        code="MALFORMED_LIFECYCLE_STATUS",
        unsupported_code="UNSUPPORTED_CRITICAL_LIFECYCLE_QUALIFIER",
        understood=understood_critical,
    )
    return {
        "target": target,
        "event": event,
        "status_authority": status_authority,
        "effective_at": effective_at,
        "sequence": sequence,
        "scope": scope,
        "next_update": next_update,
        "reason": reason,
        "critical": critical,
    }


def _target_equal(left: tuple[str, Any], right: tuple[str, Any]) -> bool:
    return left == right


def _evaluate_lifecycle(payload: Mapping[str, Any]) -> dict[str, Any]:
    target = _lifecycle_target(payload["target"])
    understood = frozenset(payload.get("understood_critical_qualifiers", ()))
    statuses_raw = payload.get("statuses", ())
    if not isinstance(statuses_raw, (tuple, list)):
        raise _malformed("statuses MUST be an array", "MALFORMED_LIFECYCLE_INPUT")
    if len(statuses_raw) > 64:
        raise _malformed("lifecycle evidence exceeds implementation limit", "RESOURCE_LIMIT_EXCEEDED")
    evaluation_time = payload.get("evaluation_time")
    evaluation_instant = None
    if evaluation_time is not None:
        if not is_rfc3339(evaluation_time):
            raise _malformed("evaluation_time MUST be RFC 3339", "MALFORMED_EVALUATION_CONTEXT")
        evaluation_instant = parse_rfc3339(evaluation_time)
    required_scope = payload.get("required_scope")
    if required_scope is not None:
        required_scope = _uri(required_scope, "MALFORMED_EVALUATION_CONTEXT", "required_scope")

    accepted: list[dict[str, Any]] = []
    for index, raw in enumerate(statuses_raw):
        status = _lifecycle_status(raw, understood_critical=understood)
        if not _target_equal(status["target"], target):
            continue
        if required_scope is not None and status["scope"] != required_scope:
            continue
        effective = "NO_DECLARED_TIME"
        if status["effective_at"] is not None and evaluation_instant is not None:
            effective = (
                "EFFECTIVE"
                if parse_rfc3339(status["effective_at"]) <= evaluation_instant
                else "STATUS_EVENT_NOT_YET_EFFECTIVE"
            )
        elif status["effective_at"] is not None:
            effective = "NOT_EVALUATED"
        freshness = "NOT_EVALUATED"
        if status["next_update"] is not None and evaluation_instant is not None:
            freshness = (
                "STALE_BY_SOURCE"
                if evaluation_instant > parse_rfc3339(status["next_update"])
                else "WITHIN_SOURCE_WINDOW"
            )
        accepted.append(
            {
                "index": index,
                "event": status["event"],
                "status_authority": status["status_authority"],
                "sequence": status["sequence"],
                "scope": status["scope"],
                "effective": effective,
                "freshness": freshness,
            }
        )

    conflicts: list[str] = []
    seen_sequences: dict[tuple[Any, ...], tuple[Any, ...]] = {}
    for status in accepted:
        if status["sequence"] is None:
            continue
        key = (status["status_authority"], tuple(_target_json(target)), status["scope"], status["sequence"])
        material = (status["event"], status["effective"], status["freshness"])
        previous = seen_sequences.get(key)
        if previous is not None and previous != material and "STATUS_SEQUENCE_CONFLICT" not in conflicts:
            conflicts.append("STATUS_SEQUENCE_CONFLICT")
        else:
            seen_sequences[key] = material

    freshness_values = {item["freshness"] for item in accepted}
    if "STALE_BY_SOURCE" in freshness_values:
        freshness = "STALE"
    elif "WITHIN_SOURCE_WINDOW" in freshness_values:
        freshness = "FRESHNESS_SIGNAL_PRESENT"
    else:
        freshness = "NOT_EVALUATED"

    return {
        "target": _target_json(target),
        "events": accepted,
        "conflicts": conflicts,
        "freshness": freshness,
        "completeness": "UNKNOWN",
        "source_authority": "NOT_EVALUATED",
        "operational_state": "INDETERMINATE",
        "absence_is_active": False,
    }


def evaluate_authority_lifecycle(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Execute the deterministic M21 semantic slice.

    ``mode`` selects one statement/evaluation surface while the single capability
    keeps the conformance profile explicitly scoped to Specifications 0006/0007.
    """

    if not isinstance(payload, Mapping):
        raise _malformed("input MUST be a map", "MALFORMED_INPUT")
    mode = payload.get("mode")
    if mode == "principal_relation":
        result = _principal_relation(
            payload["statement"],
            understood_critical=frozenset(payload.get("understood_critical_qualifiers", ())),
        )
        return {"kind": "principal_relation", **result}
    if mode == "authority_grant":
        grant = _authority_grant(
            payload["statement"],
            understood_constraints=frozenset(payload.get("understood_constraints", ())),
        )
        return {"kind": "authority_grant", **_grant_output(grant, payload.get("evaluation_time"))}
    if mode == "delegation":
        return {"kind": "delegation", **_delegation(payload)}
    if mode == "authority_status":
        result = _authority_status(
            payload["statement"],
            understood_critical=frozenset(payload.get("understood_critical_qualifiers", ())),
        )
        return {"kind": "authority_status", **result}
    if mode == "lifecycle":
        return {"kind": "lifecycle", **_evaluate_lifecycle(payload)}
    raise UnsupportedFeatureError("unsupported M21 operation mode", code="UNSUPPORTED_AUTHORITY_LIFECYCLE_MODE")
