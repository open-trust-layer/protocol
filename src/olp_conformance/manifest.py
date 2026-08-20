"""Conformance manifest loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .strict_json import load_path


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


def _parse_cases(raw: dict[str, Any]) -> list[ConformanceCase]:
    return [ConformanceCase(id=item["id"], capability=item["capability"], category=item["category"], operation=item["operation"], vector=item["vector"], description=item.get("description", "")) for item in raw["cases"]]


def _merge_profiles(target: dict[str, tuple[str, ...]], incoming: dict[str, Any], *, source: Path) -> None:
    for key, value in incoming.items():
        normalized = tuple(value)
        if key in target and target[key] != normalized:
            raise ValueError(f"conformance profile conflict for {key}: {source}")
        target[key] = normalized


def load_manifest(path: str | Path) -> ConformanceManifest:
    """Load the base manifest plus deterministic additive fragments."""
    path = Path(path).resolve()
    raw = load_path(path)
    if raw.get("schema") != "olp-conformance-manifest-v1":
        raise ValueError("unsupported conformance manifest schema")
    if raw.get("version") != 1:
        raise ValueError("unsupported conformance manifest version")
    profiles = {key: tuple(value) for key, value in raw.get("profiles", {}).items()}
    cases = _parse_cases(raw)
    fragments_dir = path.parent / "manifests"
    if fragments_dir.is_dir():
        for fragment_path in sorted(fragments_dir.glob("*.json"), key=lambda p: p.name.encode("utf-8")):
            fragment = load_path(fragment_path)
            if fragment.get("schema") != "olp-conformance-manifest-fragment-v1":
                raise ValueError(f"unsupported conformance manifest fragment schema: {fragment_path.name}")
            if fragment.get("version") != raw["version"]:
                raise ValueError(f"conformance manifest fragment version mismatch: {fragment_path.name}")
            if fragment.get("harness_version") != raw["harness_version"]:
                raise ValueError(f"conformance manifest fragment harness mismatch: {fragment_path.name}")
            _merge_profiles(profiles, fragment.get("profiles", {}), source=fragment_path)
            cases.extend(_parse_cases(fragment))
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("conformance case ids MUST be unique")
    return ConformanceManifest(version=raw["version"], harness_version=raw["harness_version"], profiles=profiles, cases=tuple(cases), root=path.parent)


def load_vector(manifest: ConformanceManifest, case: ConformanceCase) -> dict[str, Any]:
    path = (manifest.root / case.vector).resolve()
    try:
        path.relative_to(manifest.root)
    except ValueError as exc:
        raise ValueError(f"vector escapes manifest root: {case.vector}") from exc
    return load_path(path)
