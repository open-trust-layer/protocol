from pathlib import Path

from olp_conformance.commitment import build_profile_corpus_commitment
from olp_conformance.strict_json import load_path


MANIFEST = Path("conformance/manifest.json")
RELEASE = Path("specification/releases/draft-v0.3.json")
PROFILE = "draft-v0.3-interoperable-v1"


def test_draft_v03_release_manifest_pins_exact_aggregate_corpus():
    release = load_path(RELEASE)
    commitment = build_profile_corpus_commitment(MANIFEST, PROFILE)

    assert release["schema"] == "olp-specification-set-release-v1"
    assert release["release"] == "draft-v0.3"
    assert release["status"] == "draft"
    assert release["milestone"] == 25
    assert release["input_baseline_commit"] == "115ac266d1a527e12bc72fce25aa78c0e68766cb"
    assert release["interoperable_release_profile"] == PROFILE
    assert tuple(release["accepted_capabilities"]) == commitment.capabilities
    assert release["accepted_conformance_case_count"] == len(commitment.case_ids) == 180
    assert release["conformance_suite_commitment"] == {
        "algorithm": "sha-256",
        "preimage": "OLP-CONFORMANCE-SUITE-COMMITMENT-V1",
        "digest_hex": commitment.digest_hex,
    }
    assert commitment.digest_hex == "62fe81b97e629deb67f01b809215f56ae9b553968b409d6f984df2399ce38afc"


def test_draft_v03_release_is_explicitly_wire_compatible_not_security_certified():
    release = load_path(RELEASE)
    compatibility = release["compatibility"]
    assert compatibility["previous_set_release"] == "draft-v0.2"
    assert compatibility["verified_v1_wire_compatible"] is True
    for key in (
        "record_identity_v1_changed",
        "proof_input_v1_changed",
        "eddsa_ed25519_v1_changed",
        "proof_identity_v1_changed",
        "evidence_ref_v1_changed",
        "accepted_capability_semantics_redefined",
    ):
        assert compatibility[key] is False

    security = release["security_scope"]
    assert security == {
        "external_security_audit_completed": False,
        "production_security_certification": False,
        "live_network_deployment_certified": False,
    }


def test_draft_v03_release_document_inventory_includes_spec_0014():
    release = load_path(RELEASE)
    assert release["documents"][-1] == "0014-release-profiles-and-conformance-suite-commitments.md"
    assert len(release["documents"]) == 15
