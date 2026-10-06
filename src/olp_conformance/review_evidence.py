"""Validate source-bound external-review evidence without mutating promotion state."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

EVIDENCE_SCHEMA = "olp-external-review-evidence-v1"
EVIDENCE_VERSION = 1
_SUPPORTED_GATES = frozenset(
    {"public_technical_review", "independent_external_security_review"}
)
_REQUIRED_ROOT_KEYS = frozenset(
    {
        "schema",
        "version",
        "gate",
        "review_target",
        "reviewer",
        "methodology",
        "scope",
        "findings",
        "excluded_areas",
        "residual_risks",
        "references",
        "completed",
    }
)


@dataclass(frozen=True, slots=True)
class ReviewEvidenceResult:
    gate: str
    review_target_id: str
    reviewed_commit: str
    references: tuple[str, ...]
    reviewer_name: str
    reviewer_organization: str

    def gate_payload(self) -> dict[str, object]:
        return {
            "status": "completed",
            "reviewed_commit": self.reviewed_commit,
            "references": list(self.references),
        }

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": EVIDENCE_SCHEMA,
            "version": EVIDENCE_VERSION,
            "status": "valid",
            "gate": self.gate,
            "review_target_id": self.review_target_id,
            "reviewed_commit": self.reviewed_commit,
            "reviewer": {
                "name": self.reviewer_name,
                "organization": self.reviewer_organization,
            },
            "references": list(self.references),
            "candidate_gate_payload": self.gate_payload(),
        }


def validate_external_review_evidence(
    evidence_path: str | Path,
    candidate_path: str | Path,
) -> ReviewEvidenceResult:
    """Validate one completed external review against the current frozen target.

    This function is intentionally read-only. It returns the exact gate payload that
    could be applied after project review, but never edits the candidate manifest.
    """

    evidence = _load_object(Path(evidence_path), "review evidence")
    candidate = _load_object(Path(candidate_path), "candidate manifest")

    if set(evidence) != _REQUIRED_ROOT_KEYS:
        missing = sorted(_REQUIRED_ROOT_KEYS - set(evidence))
        extra = sorted(set(evidence) - _REQUIRED_ROOT_KEYS)
        raise ValueError(f"review evidence keys mismatch: missing={missing}, extra={extra}")
    if evidence["schema"] != EVIDENCE_SCHEMA or evidence["version"] != EVIDENCE_VERSION:
        raise ValueError("unsupported review evidence schema/version")

    gate = _nonempty_text(evidence["gate"], "gate", 64)
    if gate not in _SUPPORTED_GATES:
        raise ValueError("gate is not a supported v1 external review gate")
    if evidence["completed"] is not True:
        raise ValueError("review evidence must explicitly declare completed=true")

    target = _object(evidence["review_target"], "review_target")
    if set(target) != {"id", "source_commit"}:
        raise ValueError("review_target must contain exactly id and source_commit")
    target_id = _nonempty_text(target["id"], "review_target.id", 128)
    reviewed_commit = _commit_id(target["source_commit"], "review_target.source_commit")

    candidate_target = _object(candidate.get("review_target"), "candidate.review_target")
    candidate_target_id = _nonempty_text(
        candidate_target.get("id"), "candidate.review_target.id", 128
    )
    candidate_target_commit = _commit_id(
        candidate_target.get("source_commit"), "candidate.review_target.source_commit"
    )
    if candidate_target.get("status") != "frozen":
        raise ValueError("candidate review target must be frozen before evidence intake")
    if target_id != candidate_target_id or reviewed_commit != candidate_target_commit:
        raise ValueError("review evidence does not match the exact frozen candidate target")

    external_gates = _object(candidate.get("external_gates"), "candidate.external_gates")
    if gate not in external_gates:
        raise ValueError("candidate does not declare the requested external review gate")

    reviewer = _object(evidence["reviewer"], "reviewer")
    if set(reviewer) != {"name", "organization", "independence_statement"}:
        raise ValueError(
            "reviewer must contain exactly name, organization, and independence_statement"
        )
    reviewer_name = _nonempty_text(reviewer["name"], "reviewer.name", 256)
    reviewer_organization = _nonempty_text(
        reviewer["organization"], "reviewer.organization", 256
    )
    independence = reviewer["independence_statement"]
    if not isinstance(independence, str):
        raise ValueError("reviewer.independence_statement must be text")
    independence = independence.strip()
    if len(independence) > 2000:
        raise ValueError("reviewer.independence_statement exceeds 2000 characters")
    if gate == "independent_external_security_review" and not independence:
        raise ValueError(
            "independent external security review requires an independence statement"
        )

    _text_list(evidence["methodology"], "methodology", minimum=1, maximum=64)
    _text_list(evidence["scope"], "scope", minimum=1, maximum=128)
    _text_list(evidence["excluded_areas"], "excluded_areas", minimum=0, maximum=128)
    _text_list(evidence["residual_risks"], "residual_risks", minimum=0, maximum=128)
    _validate_findings(evidence["findings"])
    references = _reference_list(evidence["references"])

    return ReviewEvidenceResult(
        gate=gate,
        review_target_id=target_id,
        reviewed_commit=reviewed_commit,
        references=references,
        reviewer_name=reviewer_name,
        reviewer_organization=reviewer_organization,
    )


def _validate_findings(value: object) -> None:
    if not isinstance(value, list) or len(value) > 256:
        raise ValueError("findings must be an array with at most 256 entries")
    ids: set[str] = set()
    for index, item in enumerate(value):
        finding = _object(item, f"findings[{index}]")
        if set(finding) != {"id", "severity", "summary", "disposition"}:
            raise ValueError(
                f"findings[{index}] must contain exactly id, severity, summary, and disposition"
            )
        finding_id = _nonempty_text(finding["id"], f"findings[{index}].id", 128)
        if finding_id in ids:
            raise ValueError("finding ids must be unique")
        ids.add(finding_id)
        severity = _nonempty_text(
            finding["severity"], f"findings[{index}].severity", 16
        ).casefold()
        if severity not in {"informational", "low", "medium", "high", "critical"}:
            raise ValueError(f"findings[{index}].severity is unsupported")
        _nonempty_text(finding["summary"], f"findings[{index}].summary", 4000)
        disposition = _nonempty_text(
            finding["disposition"], f"findings[{index}].disposition", 32
        ).casefold()
        if disposition not in {"resolved", "accepted-residual-risk", "not-applicable"}:
            raise ValueError(f"findings[{index}].disposition is not final")
        if severity in {"high", "critical"} and disposition == "accepted-residual-risk":
            raise ValueError("high/critical findings cannot be accepted as residual risk")


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    return _object(raw, label)


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object")
    return value


def _nonempty_text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text")
    result = value.strip()
    if not result or len(result) > maximum:
        raise ValueError(f"{label} must contain 1-{maximum} characters")
    return result


def _commit_id(value: object, label: str) -> str:
    result = _nonempty_text(value, label, 40)
    if len(result) != 40 or any(char not in "0123456789abcdef" for char in result):
        raise ValueError(f"{label} must be a lowercase 40-character commit id")
    return result


def _text_list(
    value: object,
    label: str,
    *,
    minimum: int,
    maximum: int,
) -> tuple[str, ...]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} must contain {minimum}-{maximum} items")
    items = tuple(_nonempty_text(item, label, 4000) for item in value)
    if len(items) != len(set(items)):
        raise ValueError(f"{label} entries must be unique")
    return items


def _reference_list(value: object) -> tuple[str, ...]:
    references = _text_list(value, "references", minimum=1, maximum=32)
    for reference in references:
        parsed = urlparse(reference)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("references must be absolute HTTPS URLs without credentials")
        if parsed.fragment:
            raise ValueError("references must not use URL fragments")
    return references
