import json
from pathlib import Path

from olp_conformance.adapters import ReferenceAdapter
from olp_conformance.manifest import load_manifest
from olp_conformance.reporting import render_console, write_json_report
from olp_conformance.runner import ConformanceRunner


def test_json_report_has_stable_machine_readable_shape(tmp_path):
    report = ConformanceRunner(load_manifest('conformance/manifest.json'), ReferenceAdapter()).run(
        case_ids=['record.identity.spec-vector.001'], profile='core-v1'
    )
    target = tmp_path / 'report.json'
    write_json_report(report, target)
    value = json.loads(target.read_text())
    assert value['schema'] == 'olp-conformance-report-v1'
    assert value['summary'] == {
        'total': 1,
        'passed': 1,
        'failed': 0,
        'unsupported': 0,
        'errors': 0,
        'overall': 'PASS',
    }
    assert value['results'][0]['id'] == 'record.identity.spec-vector.001'
    assert value['results'][0]['status'] == 'PASS'


def test_console_report_contains_summary_and_adapter_name():
    report = ConformanceRunner(load_manifest('conformance/manifest.json'), ReferenceAdapter()).run(
        case_ids=['record.identity.spec-vector.001'], profile='core-v1'
    )
    text = render_console(report)
    assert 'Open Layer Protocol Conformance' in text
    assert 'Adapter: python-reference' in text
    assert 'Result: PASS' in text
