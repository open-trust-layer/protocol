from pathlib import Path

import pytest

from olp_conformance.manifest import load_manifest, load_vector


MANIFEST = Path('conformance/manifest.json')


def test_manifest_loads_all_cases():
    manifest = load_manifest(MANIFEST)
    assert manifest.version == 1
    assert manifest.harness_version == '0.1.0'
    assert len(manifest.cases) == 144
    assert len({case.id for case in manifest.cases}) == 144


def test_core_profile_contains_expected_capabilities():
    manifest = load_manifest(MANIFEST)
    assert set(manifest.profiles['core-v1']) == {
        'olp.record-identity.v1',
        'olp.record-commitment.sha256.v1',
        'olp.proof-input.v1',
        'olp.proof.eddsa-ed25519.v1',
        'olp.proof-verification.v1',
        'olp.proof-identity.v1',
        'olp.evidence-ref.v1',
        'olp.evidence-relationship.v1',
    }


def test_every_manifest_vector_exists_and_matches_case_metadata():
    manifest = load_manifest(MANIFEST)
    for case in manifest.cases:
        vector = load_vector(manifest, case)
        assert vector['id'] == case.id
        assert vector['capability'] == case.capability
        assert vector['category'] == case.category
        assert vector['operation'] == case.operation


def test_vector_path_cannot_escape_manifest_root(tmp_path):
    manifest_path = tmp_path / 'manifest.json'
    outside = tmp_path.parent / 'outside.json'
    outside.write_text('{}')
    manifest_path.write_text('''{
      "schema":"olp-conformance-manifest-v1",
      "version":1,
      "harness_version":"0.1.0",
      "profiles":{},
      "cases":[{"id":"x","capability":"c","category":"positive","operation":"o","vector":"../outside.json"}]
    }''')
    manifest = load_manifest(manifest_path)
    with pytest.raises(ValueError, match='escapes manifest root'):
        load_vector(manifest, manifest.cases[0])


def test_resolution_profile_is_separate_from_frozen_core():
    manifest = load_manifest(MANIFEST)
    assert set(manifest.profiles['resolution-v1']) == {'olp.resolution.v1'}
    assert 'olp.resolution.v1' not in set(manifest.profiles['core-v1'])


def test_m21_profile_is_additive_and_separate_from_frozen_core():
    manifest = load_manifest(MANIFEST)
    assert set(manifest.profiles['identity-authority-lifecycle-v1']) == {
        'olp.identity-authority-lifecycle.v1'
    }
    assert 'olp.identity-authority-lifecycle.v1' not in set(manifest.profiles['core-v1'])
    m21_cases = [case for case in manifest.cases if case.capability == 'olp.identity-authority-lifecycle.v1']
    assert len(m21_cases) == 18


def test_m22_profile_is_additive_and_separate_from_frozen_core():
    manifest = load_manifest(MANIFEST)
    assert set(manifest.profiles['privacy-disclosure-v1']) == {'olp.privacy-disclosure.v1'}
    assert 'olp.privacy-disclosure.v1' not in set(manifest.profiles['core-v1'])
    m22_cases = [case for case in manifest.cases if case.capability == 'olp.privacy-disclosure.v1']
    assert len(m22_cases) == 18


def test_m23_profile_is_additive_and_separate_from_frozen_core():
    manifest = load_manifest(MANIFEST)
    assert set(manifest.profiles['transport-encoding-v1']) == {'olp.transport-encoding.v1'}
    assert 'olp.transport-encoding.v1' not in set(manifest.profiles['core-v1'])
    m23_cases = [case for case in manifest.cases if case.capability == 'olp.transport-encoding.v1']
    assert len(m23_cases) == 22
