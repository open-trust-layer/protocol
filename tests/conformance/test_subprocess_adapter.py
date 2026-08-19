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
