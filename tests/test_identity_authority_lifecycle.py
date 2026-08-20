from __future__ import annotations

import pytest

from olp.encoding.record_identity import record_identity
from olp.errors import ConformanceError, UnsupportedFeatureError
from olp.identity_authority_lifecycle_v1 import evaluate_authority_lifecycle
from olp.model.record import RecordV1


ACTION = "urn:example:action:write"
RESOURCE = [0, "urn:example:resource:account-1"]
CONTEXT = "urn:example:context:payments"


def grant(
    grantor: str,
    grantee: str,
    *,
    delegable: bool,
    parent=None,
    action: str = ACTION,
    resource=RESOURCE,
    context: str | None = CONTEXT,
    valid_from: str | None = "2026-01-01T00:00:00Z",
    valid_until: str | None = "2027-01-01T00:00:00Z",
):
    return [
        "OLP-AUTHORITY-GRANT",
        1,
        grantor,
        grantee,
        action,
        resource,
        context,
        valid_from,
        valid_until,
        delegable,
        parent,
        {},
        {},
    ]


def lifecycle(
    target,
    event: str,
    *,
    authority: str | None = "urn:example:authority:status",
    effective_at: str | None = "2026-05-01T00:00:00Z",
    sequence: int | None = 1,
    scope: str | None = None,
    next_update: str | None = None,
):
    return [
        "OLP-LIFECYCLE-STATUS",
        1,
        target,
        event,
        authority,
        effective_at,
        sequence,
        scope,
        next_update,
        None,
        {},
        [],
    ]


def parent_record(statement) -> RecordV1:
    return RecordV1(envelope_version=1, type="authority.grant", content=statement)


def test_principal_role_is_not_authority_or_trust():
    result = evaluate_authority_lifecycle(
        {
            "mode": "principal_relation",
            "statement": [
                "OLP-PRINCIPAL-RELATION",
                1,
                "holdsRole",
                "did:example:alice",
                [2, "urn:example:role:auditor"],
                "did:example:org:acme",
                {},
                [],
            ],
        }
    )
    assert result["relation_type"] == "holdsRole"
    assert result["authority"] == "NOT_EVALUATED"
    assert result["trust"] == "NOT_EVALUATED"
    assert "authorized" not in result


def test_authority_interval_is_half_open_and_not_a_policy_decision():
    statement = grant("did:example:root", "did:example:alice", delegable=False)
    at_end = evaluate_authority_lifecycle(
        {"mode": "authority_grant", "statement": statement, "evaluation_time": "2027-01-01T00:00:00Z"}
    )
    assert at_end["temporal_applicability"] == "AFTER_DECLARED_INTERVAL"
    assert at_end["policy_decision"] == "NOT_EVALUATED"


def test_invalid_authority_interval_is_malformed():
    statement = grant(
        "did:example:root",
        "did:example:alice",
        delegable=False,
        valid_from="2027-01-01T00:00:00Z",
        valid_until="2026-01-01T00:00:00Z",
    )
    with pytest.raises(ConformanceError) as exc:
        evaluate_authority_lifecycle({"mode": "authority_grant", "statement": statement})
    assert exc.value.code == "INVALID_AUTHORITY_INTERVAL"


def test_unknown_authority_constraint_fails_closed():
    statement = grant("did:example:root", "did:example:alice", delegable=False)
    statement[11] = {"urn:example:constraint:unknown": True}
    with pytest.raises(UnsupportedFeatureError) as exc:
        evaluate_authority_lifecycle({"mode": "authority_grant", "statement": statement})
    assert exc.value.code == "UNSUPPORTED_AUTHORITY_CONSTRAINT"


def test_delegation_recomputes_parent_record_identity_and_preserves_policy_separation():
    parent_statement = grant("did:example:root", "did:example:alice", delegable=True)
    parent = parent_record(parent_statement)
    parent_ref = [0, record_identity(parent)]
    child = grant(
        "did:example:alice",
        "did:example:bob",
        delegable=False,
        parent=parent_ref,
        valid_from="2026-02-01T00:00:00Z",
        valid_until="2026-12-01T00:00:00Z",
    )
    result = evaluate_authority_lifecycle(
        {"mode": "delegation", "child": child, "parent_record": parent.__dict__ if hasattr(parent, "__dict__") else {
            "envelope_version": parent.envelope_version,
            "type": parent.type,
            "content": parent.content,
        }}
    )
    assert result["parent_identity"] == "VERIFIED"
    assert result["delegation_status"] == "SUPPORTED"
    assert result["scope"] == "WITHIN_PARENT_EXACT_BASELINE"
    assert result["policy_decision"] == "NOT_EVALUATED"


def test_delegation_rejects_parent_identity_substitution():
    parent_statement = grant("did:example:root", "did:example:alice", delegable=True)
    parent = parent_record(parent_statement)
    child = grant(
        "did:example:alice",
        "did:example:bob",
        delegable=False,
        parent=[0, b"\x99" * 32],
    )
    result = evaluate_authority_lifecycle(
        {
            "mode": "delegation",
            "child": child,
            "parent_record": {
                "envelope_version": parent.envelope_version,
                "type": parent.type,
                "content": parent.content,
            },
        }
    )
    assert result["delegation_status"] == "UNRESOLVED_PARENT"
    assert result["parent_identity"] == "MISMATCH"
    assert result["reasons"] == ["PARENT_GRANT_IDENTITY_MISMATCH"]


def test_non_delegable_parent_never_becomes_supported():
    parent_statement = grant("did:example:root", "did:example:alice", delegable=False)
    parent = parent_record(parent_statement)
    child = grant(
        "did:example:alice",
        "did:example:bob",
        delegable=False,
        parent=[0, record_identity(parent)],
    )
    result = evaluate_authority_lifecycle(
        {
            "mode": "delegation",
            "child": child,
            "parent_record": {
                "envelope_version": parent.envelope_version,
                "type": parent.type,
                "content": parent.content,
            },
        }
    )
    assert result["delegation_status"] == "NOT_SUPPORTED"
    assert "PARENT_GRANT_NOT_DELEGABLE" in result["reasons"]


def test_absence_of_lifecycle_evidence_is_not_active():
    target = ["principal", "did:example:alice"]
    result = evaluate_authority_lifecycle({"mode": "lifecycle", "target": target, "statuses": []})
    assert result["events"] == []
    assert result["completeness"] == "UNKNOWN"
    assert result["operational_state"] == "INDETERMINATE"
    assert result["absence_is_active"] is False


def test_same_sequence_conflict_is_preserved_for_record_target():
    target = ["record", [0, b"\x11" * 32]]
    statuses = [
        lifecycle(target, "suspend", sequence=7),
        lifecycle(target, "resume", sequence=7),
    ]
    result = evaluate_authority_lifecycle(
        {"mode": "lifecycle", "target": target, "statuses": statuses, "evaluation_time": "2026-06-01T00:00:00Z"}
    )
    assert result["conflicts"] == ["STATUS_SEQUENCE_CONFLICT"]
    assert [event["event"] for event in result["events"]] == ["suspend", "resume"]
    assert result["operational_state"] == "INDETERMINATE"


def test_stale_status_does_not_reverse_event_or_create_current_state():
    target = ["verificationMethod", "did:example:alice#key-1"]
    status = lifecycle(
        target,
        "revoke",
        next_update="2026-05-15T00:00:00Z",
    )
    result = evaluate_authority_lifecycle(
        {"mode": "lifecycle", "target": target, "statuses": [status], "evaluation_time": "2026-06-01T00:00:00Z"}
    )
    assert result["events"][0]["event"] == "revoke"
    assert result["events"][0]["freshness"] == "STALE_BY_SOURCE"
    assert result["freshness"] == "STALE"
    assert result["operational_state"] == "INDETERMINATE"
