"""Deterministic commitments to an exact OLP conformance profile corpus."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .manifest import load_manifest


COMMITMENT_SCHEMA = "olp-conformance-suite-commitment-v1"
COMMITMENT_VERSION = 1


@dataclass(frozen=True, slots=True)
class CorpusFileDigest:
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class ProfileCorpusCommitment:
    profile: str
    harness_version: str
    capabilities: tuple[str, ...]
    case_ids: tuple[str, ...]
    files: tuple[CorpusFileDigest, ...]
    digest_hex: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": COMMITMENT_SCHEMA,
            "version": COMMITMENT_VERSION,
            "profile": self.profile,
            "harness_version": self.harness_version,
            "capabilities": list(self.capabilities),
            "case_ids": list(self.case_ids),
            "files": [
                {"path": item.path, "sha256": item.sha256}
                for item in self.files
            ],
            "commitment": {
                "algorithm": "sha-256",
                "digest_hex": self.digest_hex,
            },
        }


def _safe_relative(root: Path, path: Path) -> str:
    root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"conformance corpus path escapes root: {path}") from exc
    return relative.as_posix()


def _canonical_payload(
    *,
    profile: str,
    harness_version: str,
    capabilities: tuple[str, ...],
    case_ids: tuple[str, ...],
    files: tuple[CorpusFileDigest, ...],
) -> bytes:
    payload = {
        "schema": COMMITMENT_SCHEMA,
        "version": COMMITMENT_VERSION,
        "profile": profile,
        "harness_version": harness_version,
        "capabilities": list(capabilities),
        "case_ids": list(case_ids),
        "files": [
            {"path": item.path, "sha256": item.sha256}
            for item in files
        ],
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build_profile_corpus_commitment(
    manifest_path: str | Path,
    profile: str,
) -> ProfileCorpusCommitment:
    """Commit to the exact corpus selected by *profile*.

    The commitment covers the base manifest, every additive manifest fragment,
    the standalone profile declaration, and each vector referenced by a case
    selected by the profile.  The canonical commitment payload also contains
    the ordered capability list and ordered selected case IDs, so selection
    semantics cannot change without changing the commitment.
    """

    manifest = load_manifest(manifest_path)
    try:
        capabilities = tuple(manifest.profiles[profile])
    except KeyError as exc:
        raise ValueError(f"unknown conformance profile: {profile}") from exc
    if not capabilities:
        raise ValueError(f"conformance profile has no capabilities: {profile}")

    capability_set = frozenset(capabilities)
    cases = tuple(case for case in manifest.cases if case.capability in capability_set)
    if not cases:
        raise ValueError(f"conformance profile selects no cases: {profile}")

    root = manifest.root.resolve()
    profile_path = root / "profiles" / f"{profile}.json"
    if not profile_path.is_file():
        raise ValueError(f"standalone profile declaration not found: {profile_path.name}")

    corpus_paths: dict[str, Path] = {}

    def add_path(path: Path) -> None:
        relative = _safe_relative(root, path)
        if relative in corpus_paths:
            return
        if not path.is_file():
            raise ValueError(f"conformance corpus file not found: {relative}")
        corpus_paths[relative] = path

    add_path(Path(manifest_path).resolve())
    fragments_dir = root / "manifests"
    if fragments_dir.is_dir():
        for fragment in sorted(fragments_dir.glob("*.json"), key=lambda p: p.name.encode("utf-8")):
            add_path(fragment)
    add_path(profile_path)

    for case in cases:
        add_path(root / case.vector)

    file_digests = tuple(
        CorpusFileDigest(
            path=relative,
            sha256=hashlib.sha256(corpus_paths[relative].read_bytes()).hexdigest(),
        )
        for relative in sorted(corpus_paths, key=lambda value: value.encode("utf-8"))
    )
    case_ids = tuple(case.id for case in cases)
    canonical = _canonical_payload(
        profile=profile,
        harness_version=manifest.harness_version,
        capabilities=capabilities,
        case_ids=case_ids,
        files=file_digests,
    )
    digest_hex = hashlib.sha256(canonical).hexdigest()
    return ProfileCorpusCommitment(
        profile=profile,
        harness_version=manifest.harness_version,
        capabilities=capabilities,
        case_ids=case_ids,
        files=file_digests,
        digest_hex=digest_hex,
    )
