"""Conformance manifest loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ConformanceCase:
    id: str
    capability: str
    category: str
    operation: str
    vector: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class ConformanceManifest:
    version: int
    harness_version: str
    profiles: dict[str, tuple[str, ...]]
    cases: tuple[ConformanceCase, ...]
    root: Path


def load_manifest(path: str | Path) -> ConformanceManifest:
    path = Path(path).resolve()
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema") != "olp-conformance-manifest-v1":
        raise ValueError("unsupported conformance manifest schema")
    if raw.get("version") != 1:
        raise ValueError("unsupported conformance manifest version")
    cases = tuple(
        ConformanceCase(
            id=item["id"],
            capability=item["capability"],
            category=item["category"],
            operation=item["operation"],
            vector=item["vector"],
            description=item.get("description", ""),
        )
        for item in raw["cases"]
    )
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("conformance case ids MUST be unique")
    return ConformanceManifest(
        version=raw["version"],
        harness_version=raw["harness_version"],
        profiles={key: tuple(value) for key, value in raw.get("profiles", {}).items()},
        cases=cases,
        root=path.parent,
    )


def load_vector(manifest: ConformanceManifest, case: ConformanceCase) -> dict[str, Any]:
    path = (manifest.root / case.vector).resolve()
    try:
        path.relative_to(manifest.root)
    except ValueError as exc:
        raise ValueError(f"vector escapes manifest root: {case.vector}") from exc
    return json.loads(path.read_text(encoding="utf-8"))
