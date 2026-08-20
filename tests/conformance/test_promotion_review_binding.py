from __future__ import annotations

import json
from pathlib import Path
import shutil

from olp_conformance.promotion import evaluate_v1_promotion


CANDIDATE = Path("stabilization/v1.0-candidate.json")


def _copy_candidate_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for name in ("conformance", "specification", "docs", "stabilization"):
        shutil.copytree(Path(name), root / name)
    return root


def test_malformed_review_target_still_produces_machine_readable_invalid_report(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["review_target"] = {"status": "frozen"}
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    report = evaluate_v1_promotion(path)
    payload = report.as_dict()

    assert report.status == "INVALID"
    assert report.internal_readiness == "FAIL"
    assert payload["review_target_id"] is None
    assert payload["review_target_status"] is None
    assert payload["review_target_source_commit"] is None
    assert next(item for item in payload["checks"] if item["id"] == "REVIEW_TARGET")["status"] == "FAIL"


def test_review_target_identifier_cannot_be_empty(tmp_path):
    root = _copy_candidate_repo(tmp_path)
    path = root / "stabilization" / "v1.0-candidate.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["review_target"] = {
        "id": "",
        "status": "preparing",
        "source_commit": None,
    }
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    report = evaluate_v1_promotion(path)
    assert report.status == "INVALID"
    assert report.review_target_id is None
