from pathlib import Path
import json
import shutil

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


def test_unrelated_future_profile_fragment_does_not_change_frozen_commitment(tmp_path):
    copied = tmp_path / "conformance"
    shutil.copytree(MANIFEST.parent, copied)
    manifest_path = copied / "manifest.json"
    before = build_profile_corpus_commitment(manifest_path, PROFILE)

    unrelated = {
        "schema": "olp-conformance-manifest-fragment-v1",
        "version": 1,
        "harness_version": "0.1.0",
        "profiles": {"future-unrelated-v1": ["urn:example:future-capability:v1"]},
        "cases": [],
    }
    (copied / "manifests" / "zzz-future-unrelated.json").write_text(
        json.dumps(unrelated, indent=2) + "\n",
        encoding="utf-8",
    )

    after = build_profile_corpus_commitment(manifest_path, PROFILE)
    assert after.digest_hex == before.digest_hex
    assert after.files == before.files


def test_standalone_profile_registry_exactly_matches_loaded_manifest_profiles():
    manifest = load_manifest(MANIFEST)
    profile_dir = MANIFEST.parent / "profiles"
    paths = sorted(profile_dir.glob("*.json"), key=lambda item: item.name.encode("utf-8"))
    assert {path.stem for path in paths} == set(manifest.profiles)

    for path in paths:
        raw = load_path(path)
        assert set(raw) == {"schema", "id", "version", "status", "capabilities"}, path.name
        assert raw["schema"] == "olp-conformance-profile-v1"
        assert raw["version"] == 1
        assert raw["status"] == "draft-v0.3"
        assert raw["id"] == path.stem
        assert len(raw["capabilities"]) == len(set(raw["capabilities"]))
        assert tuple(raw["capabilities"]) == manifest.profiles[raw["id"]]


def test_frozen_profiles_are_pinned_to_their_accepted_case_ids():
    """A frozen profile's corpus is its pinned list, not a capability sweep."""
    from olp_conformance.commitment import frozen_case_ids

    root = MANIFEST.parent
    assert frozen_case_ids(root, "core-v1") is not None
    assert len(frozen_case_ids(root, "core-v1")) == 62
    assert len(frozen_case_ids(root, "draft-v0.3-interoperable-v1")) == 180
    # A living profile is not pinned and keeps growing with the corpus.
    assert frozen_case_ids(root, "resolution-v1") is None


def test_new_case_for_a_selected_capability_cannot_perturb_a_frozen_profile():
    """The regression barrier for review finding F-1.

    conformance/manifests/resolution-v1-private-address-forms.json adds five
    cases carrying olp.resolution.v1, a capability held by the frozen
    draft-v0.3-interoperable-v1 profile. Under capability selection those cases
    were absorbed into that profile and changed its published commitment, so
    adding regression coverage for a defect silently rewrote an accepted release
    identity. Pinning keeps the accepted corpus fixed while the living
    resolution-v1 profile picks the new coverage up.
    """
    frozen = build_profile_corpus_commitment(MANIFEST, "draft-v0.3-interoperable-v1")
    assert len(frozen.case_ids) == 180
    assert frozen.digest_hex == (
        "62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc"
    )
    added = {f"resolution.network.private-address.{n:03d}" for n in range(2, 7)}
    assert added.isdisjoint(frozen.case_ids)

    core = build_profile_corpus_commitment(MANIFEST, "core-v1")
    assert len(core.case_ids) == 62
    assert core.digest_hex == (
        "8b45732541679f179d0eeeb2e94e1730b1b03da55cf910e64157358361b45b5e"
    )

    living = build_profile_corpus_commitment(MANIFEST, "resolution-v1")
    assert len(living.case_ids) == 21
    assert "resolution.network.private-address.002" in living.case_ids
