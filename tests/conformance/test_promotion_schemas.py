import json
from pathlib import Path


SCHEMAS = Path("stabilization/schemas")
CANDIDATE_SCHEMA_V1 = SCHEMAS / "v1-promotion-candidate.schema.json"
CANDIDATE_SCHEMA = SCHEMAS / "v2-promotion-candidate.schema.json"
REVIEW_SCHEMA = SCHEMAS / "v1-review-register.schema.json"
REPORT_SCHEMA_V1 = SCHEMAS / "v1-promotion-report.schema.json"
REPORT_SCHEMA = SCHEMAS / "v2-promotion-report.schema.json"
CANDIDATE = Path("stabilization/v1.0-candidate.json")
REVIEW = Path("stabilization/v1-review-register.json")
CHECKED_IN_REVIEW_COMMIT = "d470970180bfa128ca14fd01ac920c95dd8ec288"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_historical_v1_promotion_schemas_remain_available():
    assert CANDIDATE_SCHEMA_V1.is_file()
    assert REPORT_SCHEMA_V1.is_file()
    assert _load(CANDIDATE_SCHEMA_V1)["properties"]["schema"]["const"] == "olp-v1-promotion-candidate-v1"
    assert _load(REPORT_SCHEMA_V1)["properties"]["schema"]["const"] == "olp-v1-promotion-report-v1"


def test_candidate_v2_schema_has_no_review_waiver_state():
    schema = _load(CANDIDATE_SCHEMA)
    gates = schema["properties"]["external_gates"]["properties"]
    for gate in gates.values():
        assert gate == {"$ref": "#/$defs/externalGate"}
    assert schema["$defs"]["externalGate"]["properties"]["status"]["enum"] == [
        "pending",
        "completed",
    ]
    assert schema["$defs"]["reviewTarget"]["properties"]["status"]["enum"] == [
        "preparing",
        "frozen",
    ]
    assert "waived" not in CANDIDATE_SCHEMA.read_text(encoding="utf-8").lower()


def test_candidate_v2_schema_requires_snapshot_binding_fields():
    schema = _load(CANDIDATE_SCHEMA)
    assert "review_target" in schema["required"]
    assert schema["properties"]["review_target"] == {"$ref": "#/$defs/reviewTarget"}
    external = schema["$defs"]["externalGate"]
    assert external["required"] == ["status", "reviewed_commit", "references"]
    assert "reviewed_commit" in external["properties"]


def test_promotion_report_v2_schema_locks_readiness_and_supports_invalid_target_diagnostics():
    schema = _load(REPORT_SCHEMA)
    assert schema["properties"]["internal_readiness"]["enum"] == ["PASS", "FAIL"]
    assert schema["properties"]["status"]["enum"] == ["INVALID", "BLOCKED", "READY"]
    target_status = schema["properties"]["review_target_status"]["oneOf"]
    assert {"enum": ["preparing", "frozen"]} in target_status
    assert {"type": "null"} in target_status
    target_id = schema["properties"]["review_target_id"]["oneOf"]
    assert {"type": "null"} in target_id
    assert schema["properties"]["checks"]["items"]["properties"]["status"]["enum"] == [
        "PASS",
        "FAIL",
        "BLOCKED",
    ]


def test_review_schema_cannot_mark_open_finding_as_an_unknown_status():
    schema = _load(REVIEW_SCHEMA)
    finding = schema["properties"]["findings"]["items"]
    assert finding["properties"]["status"]["enum"] == ["open", "resolved"]
    assert finding["properties"]["severity"]["enum"] == ["low", "medium", "high", "critical"]


def test_checked_in_candidate_v2_is_frozen_review2_snapshot_bound_external_review():
    candidate = _load(CANDIDATE)
    assert candidate["schema"] == "olp-v1-promotion-candidate-v2"
    assert candidate["version"] == 2
    assert candidate["status"] == "candidate"
    assert candidate["review_target"] == {
        "id": "olp-v1.0-review-2",
        "status": "frozen",
        "source_commit": CHECKED_IN_REVIEW_COMMIT,
    }
    for gate in candidate["external_gates"].values():
        assert gate == {"status": "pending", "reviewed_commit": None, "references": []}


def test_checked_in_review_register_is_pinned_to_draft_v03_baseline():
    review = _load(REVIEW)
    assert review["schema"] == "olp-v1-review-register-v1"
    assert review["baseline_release"] == "draft-v0.3"
    assert review["baseline_commit"] == "5acc4b8934305a5215379c480db32bd0fd22f3ae"
    assert review["findings"]
    assert all(item["status"] == "resolved" for item in review["findings"])
