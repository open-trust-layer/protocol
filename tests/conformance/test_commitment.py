from pathlib import Path

from olp_conformance.commitment import build_profile_corpus_commitment
from olp_conformance.manifest import load_manifest
from olp_conformance.strict_json import load_path


MANIFEST = Path("conformance/manifest.json")
PROFILE = "draft-v0.3-interoperable-v1"


def test_draft_v03_corpus_commitment_is_deterministic_and_complete():
    first = build_profile_corpus_commitment(MANIFEST, PROFILE)
    second = build_profile_corpus_commitment(MANIFEST, PROFILE)
    assert first == second
    assert len(first.capabilities) == 15
    assert len(first.case_ids) == 180
    assert len(set(first.case_ids)) == 180
    assert len(first.digest_hex) == 64
    assert first.digest_hex == first.digest_hex.lower()
    paths = [item.path for item in first.files]
    assert paths == sorted(paths, key=lambda value: value.encode("utf-8"))
    assert len(paths) == len(set(paths))
    assert "manifest.json" in paths
    assert "manifests/draft-v0.3-interoperable-v1.json" in paths
    assert "profiles/draft-v0.3-interoperable-v1.json" in paths
    assert any(path.startswith("vectors/") for path in paths)


def test_different_profiles_have_different_corpus_commitments():
    aggregate = build_profile_corpus_commitment(MANIFEST, PROFILE)
    core = build_profile_corpus_commitment(MANIFEST, "core-v1")
    assert aggregate.digest_hex != core.digest_hex
    assert len(core.case_ids) == 62


def test_standalone_profile_registry_matches_loaded_manifest_profiles():
    manifest = load_manifest(MANIFEST)
    profile_dir = MANIFEST.parent / "profiles"
    for path in sorted(profile_dir.glob("*.json"), key=lambda item: item.name.encode("utf-8")):
        raw = load_path(path)
        assert set(raw) == {"schema", "id", "version", "status", "capabilities"}, path.name
        assert raw["schema"] == "olp-conformance-profile-v1"
        assert raw["version"] == 1
        assert raw["status"] == "draft-v0.3"
        assert raw["id"] == path.stem
        assert len(raw["capabilities"]) == len(set(raw["capabilities"]))
        assert tuple(raw["capabilities"]) == manifest.profiles[raw["id"]]
