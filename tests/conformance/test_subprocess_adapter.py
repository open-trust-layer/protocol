import os
import sys
from pathlib import Path

from olp_conformance.adapter import SubprocessAdapter
from olp_conformance.manifest import load_manifest
from olp_conformance.runner import ConformanceRunner


def test_subprocess_adapter_contract_runs_reference_implementation():
    command = [sys.executable, '-m', 'olp_conformance.subprocess_reference']
    adapter = SubprocessAdapter(command, timeout=10, env={'PYTHONPATH': str(Path('src').resolve())})
    capabilities = adapter.capabilities()
    assert 'olp.record-identity.v1' in capabilities

    report = ConformanceRunner(load_manifest('conformance/manifest.json'), adapter).run(
        case_ids=['record.identity.spec-vector.001', 'proof.verify.negative.signature.001'],
        profile='core-v1',
    )
    assert report.total == 2
    assert report.overall == 'PASS'


def test_reference_subprocess_rejects_duplicate_request_properties():
    import json
    import subprocess

    raw = '{"protocol":"olp-conformance-adapter-v1","operation":"capabilities","operation":"evil","input":{}}\n'
    completed = subprocess.run(
        [sys.executable, '-m', 'olp_conformance.subprocess_reference'],
        input=raw,
        text=True,
        capture_output=True,
        env={**os.environ, 'PYTHONPATH': str(Path('src').resolve())},
        check=True,
    )
    response = json.loads(completed.stdout)
    assert response['ok'] is False
    assert response['error']['classification'] == 'MALFORMED'
    assert response['error']['reason'] == 'INVALID_JSON'
