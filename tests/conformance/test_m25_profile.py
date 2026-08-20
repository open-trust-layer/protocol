from pathlib import Path

from olp_conformance.adapters import ReferenceAdapter
from olp_conformance.manifest import load_manifest
from olp_conformance.results import CaseStatus
from olp_conformance.runner import ConformanceRunner


MANIFEST = Path("conformance/manifest.json")
PROFILE = "draft-v0.3-interoperable-v1"


def test_python_draft_v03_aggregate_profile_passes_all_accepted_cases():
    manifest = load_manifest(MANIFEST)
    report = ConformanceRunner(manifest, ReferenceAdapter()).run(profile=PROFILE)
    assert len(report.results) == 180
    failed = [item for item in report.results if item.status is not CaseStatus.PASS]
    assert not failed, [(item.id, item.status.value, item.message) for item in failed]


def test_draft_v03_aggregate_profile_has_exact_accepted_capability_set():
    manifest = load_manifest(MANIFEST)
    assert manifest.profiles[PROFILE] == (
        "olp.record-identity.v1",
        "olp.record-commitment.sha256.v1",
        "olp.proof-input.v1",
        "olp.proof.eddsa-ed25519.v1",
        "olp.proof-verification.v1",
        "olp.proof-identity.v1",
        "olp.evidence-ref.v1",
        "olp.evidence-relationship.v1",
        "olp.bundle.v1",
        "olp.resolution.v1",
        "olp.identity-authority-lifecycle.v1",
        "olp.privacy-disclosure.v1",
        "olp.transport-encoding.v1",
        "olp.streaming-transport.v1",
        "olp.http-api.v1",
    )
