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


def test_cli_review_evidence_check_json(tmp_path, capsys):
    evidence = tmp_path / 'review.json'
    evidence.write_text(json.dumps({
        'schema': 'olp-external-review-evidence-v1',
        'version': 1,
        'gate': 'public_technical_review',
        'review_target': {
            'id': 'olp-v1.0-review-4',
            'source_commit': 'c293c5524318b342149a80c3e0322e29742f44f7',
        },
        'reviewer': {
            'name': 'External Reviewer',
            'organization': 'Review Lab',
            'independence_statement': '',
        },
        'methodology': ['specification review'],
        'scope': ['review-4 frozen source'],
        'findings': [],
        'excluded_areas': [],
        'residual_risks': [],
        'references': ['https://example.org/review/olp-review-4'],
        'completed': True,
    }), encoding='utf-8')

    assert main([
        'review-evidence-check',
        '--candidate', 'stabilization/v1.0-candidate.json',
        '--evidence', str(evidence),
        '--json',
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload['status'] == 'valid'
    assert payload['candidate_gate_payload'] == {
        'status': 'completed',
        'reviewed_commit': 'c293c5524318b342149a80c3e0322e29742f44f7',
        'references': ['https://example.org/review/olp-review-4'],
    }
