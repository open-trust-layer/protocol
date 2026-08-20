"""Security-hardened executable entry point for Milestone 21.

The structural parsers live in :mod:`olp.identity_authority_lifecycle`.  This
entry point adds the graph-sensitive checks that require enclosing Record
Identity verification and uses a hashable exact lifecycle-target key for
sequence conflict detection.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from . import identity_authority_lifecycle as core
from .encoding.record_identity import record_identity
from .errors import ConformanceError, UnsupportedFeatureError
from .model.proof import is_rfc3339, parse_rfc3339
from .model.record import RecordV1


def _parent_record(value: Any) -> RecordV1:
    if not isinstance(value, Mapping):
        raise ConformanceError("parent_record MUST be a RecordV1 map", code="MALFORMED_DELEGATION_INPUT")
    record = RecordV1.from_mapping(value)
    record.validate()
    return record


def _delegation(payload: Mapping[str, Any]) -> dict[str, Any]:
    understood = frozenset(payload.get("understood_constraints", ()))
    child = core._authority_grant(payload["child"], understood_constraints=understood)
    claimed_parent = child["parent_grant"]
    if claimed_parent is None:
        return {
            "kind": "delegation",
            "delegation_status": "NO_PARENT_CLAIMED",
            "reasons": [],
            "scope": "NOT_EVALUATED",
            "parent_identity": "NOT_APPLICABLE",
            "policy_decision": "NOT_EVALUATED",
        }
    if "parent_record" not in payload:
        return {
            "kind": "delegation",
            "delegation_status": "UNRESOLVED_PARENT",
            "reasons": ["PARENT_GRANT_UNRESOLVED"],
            "scope": "INDETERMINATE",
            "parent_identity": "UNRESOLVED",
            "policy_decision": "NOT_EVALUATED",
        }

    record = _parent_record(payload["parent_record"])
    computed_parent = (0, record_identity(record))
    if computed_parent != claimed_parent:
        return {
            "kind": "delegation",
            "delegation_status": "UNRESOLVED_PARENT",
            "reasons": ["PARENT_GRANT_IDENTITY_MISMATCH"],
            "scope": "INDETERMINATE",
            "parent_identity": "MISMATCH",
            "computed_parent_reference": core._ref_json(computed_parent),
            "policy_decision": "NOT_EVALUATED",
        }

    try:
        parent = core._authority_grant(record.content, understood_constraints=understood)
    except (ConformanceError, UnsupportedFeatureError) as exc:
        raise ConformanceError(
            "referenced parent record is not a supported AuthorityGrantStatementV1",
            code="PARENT_GRANT_TYPE_MISMATCH",
        ) from exc

    reasons: list[str] = []
    exact_scope = True
    if parent["grantee"] != child["grantor"]:
        reasons.append("DELEGATION_PRINCIPAL_MISMATCH")
    if not parent["delegable"]:
        reasons.append("PARENT_GRANT_NOT_DELEGABLE")
    if parent["action"] != child["action"]:
        reasons.append("DELEGATION_ACTION_SCOPE_MISMATCH")
        exact_scope = False
    if not core._resource_equal(parent["resource"], child["resource"]):
        reasons.append("DELEGATION_RESOURCE_SCOPE_MISMATCH")
        exact_scope = False
    if parent["context"] != child["context"]:
        reasons.append("DELEGATION_CONTEXT_SCOPE_MISMATCH")
        exact_scope = False
    if not core._interval_within(parent, child):
        reasons.append("DELEGATION_TIME_SCOPE_MISMATCH")
        exact_scope = False
    if parent["constraints"] != child["constraints"]:
        reasons.append("DELEGATION_CONSTRAINT_SCOPE_INDETERMINATE")
        exact_scope = False

    return {
        "kind": "delegation",
        "delegation_status": "SUPPORTED" if not reasons else "NOT_SUPPORTED",
        "reasons": reasons,
        "scope": "WITHIN_PARENT_EXACT_BASELINE" if exact_scope else "OUTSIDE_OR_INDETERMINATE",
        "parent_identity": "VERIFIED",
        "parent_reference": core._ref_json(computed_parent),
        "policy_decision": "NOT_EVALUATED",
    }


def _target_key(target: tuple[str, Any]) -> tuple[Any, ...]:
    if target[0] in {"record", "proof"}:
        kind, digest = target[1]
        return target[0], kind, digest
    return target[0], target[1]


def _lifecycle(payload: Mapping[str, Any]) -> dict[str, Any]:
    target = core._lifecycle_target(payload["target"])
    understood = frozenset(payload.get("understood_critical_qualifiers", ()))
    statuses_raw = payload.get("statuses", ())
    if not isinstance(statuses_raw, (tuple, list)):
        raise ConformanceError("statuses MUST be an array", code="MALFORMED_LIFECYCLE_INPUT")
    if len(statuses_raw) > 64:
        raise ConformanceError("lifecycle evidence exceeds implementation limit", code="RESOURCE_LIMIT_EXCEEDED")

    evaluation_time = payload.get("evaluation_time")
    evaluation_instant = None
    if evaluation_time is not None:
        if not is_rfc3339(evaluation_time):
            raise ConformanceError("evaluation_time MUST be RFC 3339", code="MALFORMED_EVALUATION_CONTEXT")
        evaluation_instant = parse_rfc3339(evaluation_time)
    required_scope = payload.get("required_scope")
    if required_scope is not None:
        required_scope = core._uri(required_scope, "MALFORMED_EVALUATION_CONTEXT", "required_scope")

    accepted: list[dict[str, Any]] = []
    for index, raw in enumerate(statuses_raw):
        status = core._lifecycle_status(raw, understood_critical=understood)
        if not core._target_equal(status["target"], target):
            continue
        if required_scope is not None and status["scope"] != required_scope:
            continue

        if status["effective_at"] is None:
            effective = "NO_DECLARED_TIME"
        elif evaluation_instant is None:
            effective = "NOT_EVALUATED"
        else:
            effective = (
                "EFFECTIVE"
                if parse_rfc3339(status["effective_at"]) <= evaluation_instant
                else "STATUS_EVENT_NOT_YET_EFFECTIVE"
            )

        if status["next_update"] is None or evaluation_instant is None:
            freshness = "NOT_EVALUATED"
        else:
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
    target_key = _target_key(target)
    for status in accepted:
        if status["sequence"] is None:
            continue
        key = (status["status_authority"], target_key, status["scope"], status["sequence"])
        material = (status["event"], status["effective"], status["freshness"])
        previous = seen_sequences.get(key)
        if previous is not None and previous != material:
            if "STATUS_SEQUENCE_CONFLICT" not in conflicts:
                conflicts.append("STATUS_SEQUENCE_CONFLICT")
        else:
            seen_sequences[key] = material

    freshness_values = {item["freshness"] for item in accepted}
    freshness = (
        "STALE"
        if "STALE_BY_SOURCE" in freshness_values
        else "FRESHNESS_SIGNAL_PRESENT"
        if "WITHIN_SOURCE_WINDOW" in freshness_values
        else "NOT_EVALUATED"
    )
    return {
        "kind": "lifecycle",
        "target": core._target_json(target),
        "events": accepted,
        "conflicts": conflicts,
        "freshness": freshness,
        "completeness": "UNKNOWN",
        "source_authority": "NOT_EVALUATED",
        "operational_state": "INDETERMINATE",
        "absence_is_active": False,
    }


def evaluate_authority_lifecycle(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ConformanceError("input MUST be a map", code="MALFORMED_INPUT")
    mode = payload.get("mode")
    if mode == "delegation":
        return _delegation(payload)
    if mode == "lifecycle":
        return _lifecycle(payload)
    return core.evaluate_authority_lifecycle(payload)
