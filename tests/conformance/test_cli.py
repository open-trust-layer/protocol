import json
from pathlib import Path

from olp_conformance.cli import main


def test_cli_run_writes_report(tmp_path, capsys):
    target = tmp_path / 'report.json'
    code = main([
        'run', '--manifest', 'conformance/manifest.json', '--adapter', 'reference',
        '--profile', 'core-v1', '--case', 'proof.input.spec-vector.001', '--report', str(target)
    ])
    assert code == 0
    assert target.exists()
    assert json.loads(target.read_text())['summary']['overall'] == 'PASS'
    assert 'Result: PASS' in capsys.readouterr().out


def test_cli_broken_adapter_returns_nonzero(tmp_path):
    target = tmp_path / 'broken.json'
    code = main([
        'run', '--manifest', 'conformance/manifest.json', '--adapter', 'broken',
        '--profile', 'core-v1', '--case', 'record.identity.spec-vector.001', '--report', str(target), '--quiet'
    ])
    assert code == 1
    assert json.loads(target.read_text())['summary']['overall'] == 'FAIL'


def test_cli_list_json(capsys):
    assert main(['list', '--manifest', 'conformance/manifest.json', '--json']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert 'core-v1' in payload['profiles']
    assert any(case['id'] == 'proof.input.spec-vector.001' for case in payload['cases'])
