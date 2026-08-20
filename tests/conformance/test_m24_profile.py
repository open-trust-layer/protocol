from pathlib import Path

from olp_conformance.adapters.m24 import ReferenceAdapter
from olp_conformance.manifest import load_manifest
from olp_conformance.results import CaseStatus
from olp_conformance.runner import ConformanceRunner


MANIFEST = Path("conformance/manifest.json")


def test_python_m24_streaming_http_profile_passes_all_fixed_cases():
    manifest = load_manifest(MANIFEST)
    report = ConformanceRunner(manifest, ReferenceAdapter()).run(profile="streaming-http-v1")
    assert len(report.results) == 36
    failed = [item for item in report.results if item.status is not CaseStatus.PASS]
    assert not failed, [(item.id, item.status.value, item.message) for item in failed]
