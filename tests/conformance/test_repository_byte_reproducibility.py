from __future__ import annotations

import json
from pathlib import Path

from olp_conformance.commitment import build_profile_corpus_commitment
from olp_conformance.promotion import evaluate_v1_promotion


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "conformance" / "manifest.json"
CANDIDATE = ROOT / "stabilization" / "v1.0-candidate.json"
CORE_COMMITMENT = "8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e"
RELEASE_COMMITMENT = "62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc"
TEXT_SUFFIXES = {".json", ".md", ".py", ".rs", ".toml", ".txt", ".yaml", ".yml"}


def _hash_critical_paths() -> set[Path]:
    paths: set[Path] = set()
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    for item in candidate["required_artifacts"].values():
        paths.add(ROOT / item["path"])

    for profile in ("core-v1", "draft-v0.3-interoperable-v1"):
        commitment = build_profile_corpus_commitment(MANIFEST, profile)
        for item in commitment.files:
            paths.add(MANIFEST.parent / item.path)
    return paths


def test_repository_declares_deterministic_lf_checkout_policy():
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    effective = {line.strip() for line in attributes if line.strip() and not line.lstrip().startswith("#")}
    assert "* text=auto eol=lf" in effective


def test_hash_critical_text_files_are_materialized_with_lf_bytes():
    for path in sorted(_hash_critical_paths(), key=lambda item: item.as_posix().encode("utf-8")):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        data = path.read_bytes()
        assert b"\r\n" not in data, f"hash-critical text file has CRLF working-tree bytes: {path.relative_to(ROOT)}"


def test_published_commitments_and_promotion_artifacts_reproduce_from_checkout_bytes():
    core = build_profile_corpus_commitment(MANIFEST, "core-v1")
    release = build_profile_corpus_commitment(MANIFEST, "draft-v0.3-interoperable-v1")
    report = evaluate_v1_promotion(CANDIDATE)

    assert core.digest_hex == CORE_COMMITMENT
    assert release.digest_hex == RELEASE_COMMITMENT
    assert report.internal_readiness == "PASS"
    assert report.status == "BLOCKED"
