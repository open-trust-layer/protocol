from pathlib import Path
import json
import pytest
from olp_conformance.manifest import load_manifest


def _base(root: Path) -> Path:
    p=root/'manifest.json'
    p.write_text(json.dumps({'schema':'olp-conformance-manifest-v1','version':1,'harness_version':'0.1.0','profiles':{'p':['a']},'cases':[{'id':'base','capability':'a','category':'positive','operation':'x','vector':'v.json'}]}))
    (root/'v.json').write_text('{}')
    (root/'manifests').mkdir()
    return p


def test_fragment_duplicate_case_id_fails_closed(tmp_path):
    p=_base(tmp_path)
    (tmp_path/'manifests'/'x.json').write_text(json.dumps({'schema':'olp-conformance-manifest-fragment-v1','version':1,'harness_version':'0.1.0','profiles':{},'cases':[{'id':'base','capability':'b','category':'positive','operation':'y','vector':'v.json'}]}))
    with pytest.raises(ValueError, match='case ids MUST be unique'):
        load_manifest(p)


def test_fragment_cannot_redefine_profile_incompatibly(tmp_path):
    p=_base(tmp_path)
    (tmp_path/'manifests'/'x.json').write_text(json.dumps({'schema':'olp-conformance-manifest-fragment-v1','version':1,'harness_version':'0.1.0','profiles':{'p':['b']},'cases':[]}))
    with pytest.raises(ValueError, match='profile conflict'):
        load_manifest(p)
