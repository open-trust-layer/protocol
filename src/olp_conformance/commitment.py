"""Deterministic commitments to an exact OLP conformance profile corpus."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

from .manifest import load_manifest
from .strict_json import load_path


COMMITMENT_SCHEMA = "olp-conformance-suite-commitment-v1"
COMMITMENT_VERSION = 1
COMMITMENT_DOMAIN = b"OLP-CONFORMANCE-SUITE-COMMITMENT-V1\x00"


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
                "preimage": "OLP-CONFORMANCE-SUITE-COMMITMENT-V1",
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


def _u32(value: int) -> bytes:
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("conformance commitment length/count exceeds uint32")
    return value.to_bytes(4, "big")


def _text(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return _u32(len(encoded)) + encoded


def _commitment_preimage(
    *,
    profile: str,
    harness_version: str,
    capabilities: tuple[str, ...],
    case_ids: tuple[str, ...],
    files: tuple[CorpusFileDigest, ...],
) -> bytes:
    out = bytearray(COMMITMENT_DOMAIN)
    out.extend(_text(profile))
    out.extend(_text(harness_version))
    out.extend(_u32(len(capabilities)))
    for capability in capabilities:
        out.extend(_text(capability))
    out.extend(_u32(len(case_ids)))
    for case_id in case_ids:
        out.extend(_text(case_id))
    out.extend(_u32(len(files)))
    for item in files:
        out.extend(_text(item.path))
        digest = bytes.fromhex(item.sha256)
        if len(digest) != 32:
            raise ValueError(f"invalid SHA-256 file digest length: {item.path}")
        out.extend(digest)
    return bytes(out)


def _fragment_contributes(fragment: Path, profile: str, capabilities: frozenset[str]) -> bool:
    """Return whether an additive fragment contributes to the selected corpus.

    Unrelated future profile fragments MUST NOT perturb a frozen release
    commitment. A fragment contributes when it defines the selected profile or
    contains at least one case whose capability is selected by that profile.
    Full structural validation is still performed by ``load_manifest`` before
    this helper is used.
    """

    raw = load_path(fragment)
    profiles = raw.get("profiles", {})
    if profile in profiles:
        return True
    for case in raw.get("cases", []):
        if case.get("capability") in capabilities:
            return True
    return False


def build_profile_corpus_commitment(
    manifest_path: str | Path,
    profile: str,
) -> ProfileCorpusCommitment:
    """Commit to the exact corpus selected by *profile*.

    The commitment covers the base manifest, additive manifest fragments that
    contribute to the selected profile/cases, the standalone profile
    declaration, and each vector referenced by a selected case. The preimage
    also contains the ordered capability list and ordered selected case IDs, so
    selection semantics cannot change without changing the commitment.

    Unrelated future profile fragments are intentionally excluded so a frozen
    release commitment remains stable when the repository grows additively.
    """

    manifest_path = Path(manifest_path).resolve()
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

    add_path(manifest_path)
    fragments_dir = root / "manifests"
    if fragments_dir.is_dir():
        for fragment in sorted(fragments_dir.glob("*.json"), key=lambda p: p.name.encode("utf-8")):
            if _fragment_contributes(fragment, profile, capability_set):
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
    preimage = _commitment_preimage(
        profile=profile,
        harness_version=manifest.harness_version,
        capabilities=capabilities,
        case_ids=case_ids,
        files=file_digests,
    )
    digest_hex = hashlib.sha256(preimage).hexdigest()
    return ProfileCorpusCommitment(
        profile=profile,
        harness_version=manifest.harness_version,
        capabilities=capabilities,
        case_ids=case_ids,
        files=file_digests,
        digest_hex=digest_hex,
    )
