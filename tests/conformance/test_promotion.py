from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from olp_conformance.cli import main
from olp_conformance.promotion import (
    V1_CORE_CAPABILITIES,
    V1_OPTIONAL_PROFILE_SPECS,
    evaluate_v1_promotion,
)


CANDIDATE = Path("stabilization/v1.0-candidate.json")
RELEASE_COMMITMENT = "62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc"
CORE_COMMITMENT = "8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e"
EXPECTED_BLOCKERS = (
    "PUBLIC_TECHNICAL_REVIEW_REQUIRED",
    "INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED",
)


def _copy_candidate_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for name in ("conformance", "specification", "docs", "stabilization"):
        shutil.copytree(Path(name), root / name)
    return root


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _check_statuses(report) -> dict[str, str]:
    return {item.id: item.status for item in report.checks}


def test_v1_candidate_is_internally_ready_but_externally_blocked():
    report = evaluate_v1_promotion(CANDIDATE)

    assert report.candidate == "olp-v1.0"
    assert report.baseline_release == "draft-v0.3"
    assert report.mandatory_profile == "core-v1"
    assert report.mandatory_capabilities == V1_CORE_CAPABILITIES
    assert report.optional_profiles == tuple(item[0] for item in V1_OPTIONAL_PROFILE_SPECS)
    assert len(report.optional_capabilities) == 7
    assert len(report.mandatory_capabilities + report.optional_capabilities) == 15
    assert report.release_corpus_commitment == RELEASE_COMMITMENT
    assert report.core_corpus_commitment == CORE_COMMITMENT
    assert report.internal_readiness == "PASS"
    assert report.status == "BLOCKED"
    assert report.blockers == EXPECTED_BLOCKERS
    assert "FAIL" not in _check_statuses(report).values()
    assert _check_statuses(report)["PUBLIC_TECHNICAL_REVIEW"] == "BLOCKED"
    assert _check_statuses(report)["INDEPENDENT_EXTERNAL_SECURITY_REVIEW"] == "BLOCKED"


def test_completed_external_gates_with_references_make_copy_ready(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = _load(path)
    raw["external_gates"]["public_technical_review"] = {
        "status": "completed",
        "references": ["https://example.org/olp/public-review"],
    }
    raw["external_gates"]["independent_external_security_review"] = {
        "status": "completed",
        "references": ["https://example.org/olp/security-review"],
    }
    _write(path, raw)

    report = evaluate_v1_promotion(path)
    assert report.internal_readiness == "PASS"
    assert report.status == "READY"
    assert report.blockers == ()


def test_completed_external_gate_without_reference_is_invalid(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = _load(path)
    raw["external_gates"]["public_technical_review"] = {
        "status": "completed",
        "references": [],
    }
    _write(path, raw)

    report = evaluate_v1_promotion(path)
    assert report.status == "INVALID"
    assert report.internal_readiness == "FAIL"
    assert _check_statuses(report)["PUBLIC_TECHNICAL_REVIEW"] == "FAIL"


def test_mandatory_core_cannot_be_widened_or_swapped(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = _load(path)
    raw["mandatory_profile"] = "proof-v1"
    _write(path, raw)

    report = evaluate_v1_promotion(path)
    assert report.status == "INVALID"
    assert _check_statuses(report)["MANDATORY_CORE_BOUNDARY"] == "FAIL"


def test_optional_candidate_boundary_cannot_silently_drop_profile(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = _load(path)
    raw["optional_profiles"] = raw["optional_profiles"][:-1]
    _write(path, raw)

    report = evaluate_v1_promotion(path)
    assert report.status == "INVALID"
    assert _check_statuses(report)["OPTIONAL_PROFILE_BOUNDARY"] == "FAIL"
    assert _check_statuses(report)["CANDIDATE_CAPABILITY_COVERAGE"] == "FAIL"


def test_pinned_threat_model_byte_drift_is_invalid(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    threat = root / "docs" / "v1-threat-model.md"
    threat.write_text(threat.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")

    report = evaluate_v1_promotion(root / "stabilization" / "v1.0-candidate.json")
    assert report.status == "INVALID"
    assert _check_statuses(report)["ARTIFACT_THREAT_MODEL"] == "FAIL"


def test_unresolved_normative_contradiction_blocks_internal_readiness_even_when_re_pinned(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    register = root / "stabilization" / "v1-review-register.json"
    review = _load(register)
    contradiction = next(item for item in review["findings"] if item["class"] == "normative-contradiction")
    contradiction["status"] = "open"
    _write(register, review)

    candidate_path = root / "stabilization" / "v1.0-candidate.json"
    candidate = _load(candidate_path)
    candidate["required_artifacts"]["review_register"]["sha256"] = hashlib.sha256(register.read_bytes()).hexdigest()
    _write(candidate_path, candidate)

    report = evaluate_v1_promotion(candidate_path)
    assert report.status == "INVALID"
    assert report.internal_readiness == "FAIL"
    assert _check_statuses(report)["ARTIFACT_REVIEW_REGISTER"] == "PASS"
    assert _check_statuses(report)["INTERNAL_REVIEW_REGISTER"] == "FAIL"


def test_promotion_cli_reports_blocked_as_valid_diagnostic_and_require_ready_fails(capsys):
    assert main(["promotion-check", "--candidate", str(CANDIDATE), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "BLOCKED"
    assert payload["internal_readiness"] == "PASS"
    assert payload["blockers"] == list(EXPECTED_BLOCKERS)

    assert main(["promotion-check", "--candidate", str(CANDIDATE), "--require-ready"]) == 1
    text = capsys.readouterr().out
    assert "promotion status: BLOCKED" in text
