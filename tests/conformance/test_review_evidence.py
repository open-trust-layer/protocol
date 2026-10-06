from __future__ import annotations

import json
from pathlib import Path

import pytest

from olp_conformance.review_evidence import validate_external_review_evidence

FROZEN_TARGET = "olp-v1.0-review-4"
FROZEN_COMMIT = "c293c5524318b342149a80c3e0322e29742f44f7"
CANDIDATE = Path("stabilization/v1.0-candidate.json")


def _evidence(*, gate: str = "public_technical_review") -> dict[str, object]:
    return {
        "schema": "olp-external-review-evidence-v1",
        "version": 1,
        "gate": gate,
        "review_target": {"id": FROZEN_TARGET, "source_commit": FROZEN_COMMIT},
        "reviewer": {
            "name": "External Reviewer",
            "organization": "Independent Review Lab",
            "independence_statement": "No project ownership, employment, or implementation role.",
        },
        "methodology": ["specification consistency review", "conformance reproduction"],
        "scope": ["Specifications 0001-0015", "Python and Rust interoperability evidence"],
        "findings": [
            {
                "id": "EXT-001",
                "severity": "low",
                "summary": "Editorial ambiguity was clarified without changing protocol bytes.",
                "disposition": "resolved",
            }
        ],
        "excluded_areas": ["deployment-specific operational security outside OLP"],
        "residual_risks": ["future implementation bugs remain possible"],
        "references": ["https://example.org/reviews/olp-review-4"],
        "completed": True,
    }


def _write(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "review.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_review_evidence_returns_exact_candidate_gate_payload(tmp_path: Path) -> None:
    result = validate_external_review_evidence(_write(tmp_path, _evidence()), CANDIDATE)

    assert result.review_target_id == FROZEN_TARGET
    assert result.reviewed_commit == FROZEN_COMMIT
    assert result.gate_payload() == {
        "status": "completed",
        "reviewed_commit": FROZEN_COMMIT,
        "references": ["https://example.org/reviews/olp-review-4"],
    }


def test_review_evidence_rejects_stale_source_binding(tmp_path: Path) -> None:
    payload = _evidence()
    payload["review_target"] = {
        "id": FROZEN_TARGET,
        "source_commit": "f0dd778f09f904e334477bb1d6294f78d3d466f0",
    }

    with pytest.raises(ValueError, match="exact frozen candidate target"):
        validate_external_review_evidence(_write(tmp_path, payload), CANDIDATE)


def test_security_review_requires_independence_statement(tmp_path: Path) -> None:
    payload = _evidence(gate="independent_external_security_review")
    reviewer = dict(payload["reviewer"])
    reviewer["independence_statement"] = ""
    payload["reviewer"] = reviewer

    with pytest.raises(ValueError, match="requires an independence statement"):
        validate_external_review_evidence(_write(tmp_path, payload), CANDIDATE)


def test_high_finding_cannot_be_accepted_as_residual_risk(tmp_path: Path) -> None:
    payload = _evidence()
    payload["findings"] = [
        {
            "id": "EXT-CRITICAL-001",
            "severity": "critical",
            "summary": "Material verifier bypass.",
            "disposition": "accepted-residual-risk",
        }
    ]

    with pytest.raises(ValueError, match="cannot be accepted as residual risk"):
        validate_external_review_evidence(_write(tmp_path, payload), CANDIDATE)


def test_review_evidence_requires_durable_https_reference(tmp_path: Path) -> None:
    payload = _evidence()
    payload["references"] = ["http://example.org/reviews/olp-review-4"]

    with pytest.raises(ValueError, match="absolute HTTPS URLs"):
        validate_external_review_evidence(_write(tmp_path, payload), CANDIDATE)


def test_review_evidence_requires_completed_true(tmp_path: Path) -> None:
    payload = _evidence()
    payload["completed"] = False

    with pytest.raises(ValueError, match="completed=true"):
        validate_external_review_evidence(_write(tmp_path, payload), CANDIDATE)
