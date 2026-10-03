from __future__ import annotations

import json
from pathlib import Path


def test_moon_awareness_manifest_is_metadata_only() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "moon.manifest.yaml").read_text(encoding="utf-8"))

    assert manifest["moon_version"] == "0.1"
    assert manifest["service_id"] == "olp-protocol"
    assert manifest["name"] == "Open Layer Protocol"
    assert manifest["type"] == "protocol-specification-conformance"
    assert manifest["owner"] == "Moon Core"
    assert manifest["version"] == "0.0.6.dev0"
    assert manifest["environment"] == "candidate-review"
    assert manifest["repository"] == "open-trust-layer/protocol"
    assert manifest["documentation"] == "README.md"

    assert manifest["capabilities"] == []
    assert manifest["actions"] == []
    assert manifest["dependencies"] == []
    assert manifest["health"] == {"kind": "workspace"}
    assert manifest["events"] == {"publish": [], "subscribe": []}
    assert "endpoints" not in manifest
    assert "permissions" not in manifest

    assert manifest["knowledge_domains"] == [
        "portable-verifiable-evidence",
        "protocol-conformance",
        "interoperability",
    ]
