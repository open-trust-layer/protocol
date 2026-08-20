from pathlib import Path

from olp_conformance.adapters import BrokenAdapter, ReferenceAdapter
from olp_conformance.manifest import load_manifest
from olp_conformance.results import CaseStatus
from olp_conformance.runner import ConformanceRunner


MANIFEST = load_manifest(Path('conformance/manifest.json'))


def test_reference_adapter_passes_full_core_profile():
    report = ConformanceRunner(MANIFEST, ReferenceAdapter()).run(profile='core-v1')
    assert report.total == 62
    assert report.passed == 62
    assert report.failed == 0
    assert report.unsupported == 0
    assert report.errors == 0
    assert report.overall == 'PASS'


def test_broken_adapter_is_detected():
    report = ConformanceRunner(MANIFEST, BrokenAdapter()).run(profile='core-v1')
    assert report.overall == 'FAIL'
    assert report.failed == 6
    failed_ids = {result.id for result in report.results if result.status == CaseStatus.FAIL}
    assert 'record.identity.spec-vector.001' in failed_ids
    assert 'proof.verify.negative.signature.001' in failed_ids


def test_category_filter_runs_only_negative_cases():
    report = ConformanceRunner(MANIFEST, ReferenceAdapter()).run(categories=['negative'], profile='core-v1')
    assert report.total == 11
    assert {item.category for item in report.results} == {'negative'}
    assert report.overall == 'PASS'


def test_capability_filter_runs_only_requested_capability():
    capability = 'olp.record-identity.v1'
    report = ConformanceRunner(MANIFEST, ReferenceAdapter()).run(capabilities=[capability], profile='core-v1')
    assert report.total == 9
    assert {item.capability for item in report.results} == {capability}


def test_case_filter_runs_exact_case():
    case_id = 'proof.input.spec-vector.001'
    report = ConformanceRunner(MANIFEST, ReferenceAdapter()).run(case_ids=[case_id], profile='core-v1')
    assert report.total == 1
    assert report.results[0].id == case_id
    assert report.results[0].status == CaseStatus.PASS


def test_missing_capability_reports_unsupported_not_fail():
    class MinimalAdapter:
        name = 'minimal'
        def capabilities(self):
            return frozenset({'olp.record-identity.v1'})
        def execute(self, operation, payload):
            return ReferenceAdapter().execute(operation, payload)

    report = ConformanceRunner(MANIFEST, MinimalAdapter()).run(profile='proof-v1')
    assert report.failed == 0
    assert report.unsupported == report.total
    assert report.overall == 'PARTIAL'
