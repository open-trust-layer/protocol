"""Machine-checkable OLP v1 candidate promotion gates.

This module intentionally evaluates release/stabilization metadata rather than
protocol evidence.  A green conformance corpus is necessary but not sufficient
for stable promotion: independent external security review and public technical
review remain separate required gates.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

from .commitment import build_profile_corpus_commitment
from .manifest import load_manifest
from .strict_json import load_path


CANDIDATE_SCHEMA = "olp-v1-promotion-candidate-v1"
CANDIDATE_VERSION = 1
REPORT_SCHEMA = "olp-v1-promotion-report-v1"
REPORT_VERSION = 1
REVIEW_SCHEMA = "olp-v1-review-register-v1"

V1_CORE_CAPABILITIES = (
    "olp.record-identity.v1",
    "olp.record-commitment.sha256.v1",
    "olp.proof-input.v1",
    "olp.proof.eddsa-ed25519.v1",
    "olp.proof-verification.v1",
    "olp.proof-identity.v1",
    "olp.evidence-ref.v1",
    "olp.evidence-relationship.v1",
)

V1_MANDATORY_SPECIFICATIONS = (
    "specification/0001-terminology.md",
    "specification/0002-protocol-objects.md",
    "specification/0003-record-representation.md",
    "specification/0004-proofs-and-verification.md",
    "specification/0005-evidence-relationships.md",
    "specification/0011-conformance-and-interoperability.md",
    "specification/0013-versioning-registries-and-core-profile.md",
    "specification/0014-release-profiles-and-conformance-suite-commitments.md",
    "specification/0015-stable-profile-promotion-and-readiness.md",
)

V1_OPTIONAL_PROFILE_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("bundle-v1", ("specification/0008-evidence-exchange-and-bundles.md",)),
    ("resolution-v1", ("specification/0009-resolution-and-discovery-profiles.md",)),
    (
        "identity-authority-lifecycle-v1",
        (
            "specification/0006-identity-and-authority.md",
            "specification/0007-status-and-lifecycle.md",
        ),
    ),
    (
        "privacy-disclosure-v1",
        ("specification/0010-privacy-selective-disclosure-and-data-minimization.md",),
    ),
    ("transport-encoding-v1", ("specification/0012-transport-and-api-profiles.md",)),
    ("streaming-http-v1", ("specification/0012-transport-and-api-profiles.md",)),
)

_REQUIRED_ARTIFACT_KEYS = ("threat_model", "review_register", "release_process")
_EXTERNAL_GATES = (
    ("public_technical_review", "PUBLIC_TECHNICAL_REVIEW_REQUIRED"),
    (
        "independent_external_security_review",
        "INDEPENDENT_EXTERNAL_SECURITY_REVIEW_REQUIRED",
    ),
)


@dataclass(frozen=True, slots=True)
class PromotionCheck:
    id: str
    status: str
    detail: str
    blocker: str | None = None

    def as_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "id": self.id,
            "status": self.status,
            "detail": self.detail,
        }
        if self.blocker is not None:
            value["blocker"] = self.blocker
        return value


@dataclass(frozen=True, slots=True)
class PromotionReport:
    candidate: str
    baseline_release: str
    mandatory_profile: str
    mandatory_capabilities: tuple[str, ...]
    optional_profiles: tuple[str, ...]
    optional_capabilities: tuple[str, ...]
    release_profile: str
    release_corpus_commitment: str | None
    core_corpus_commitment: str | None
    internal_readiness: str
    status: str
    blockers: tuple[str, ...]
    checks: tuple[PromotionCheck, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": REPORT_SCHEMA,
            "version": REPORT_VERSION,
            "candidate": self.candidate,
            "baseline_release": self.baseline_release,
            "mandatory_profile": self.mandatory_profile,
            "mandatory_capabilities": list(self.mandatory_capabilities),
            "optional_profiles": list(self.optional_profiles),
            "optional_capabilities": list(self.optional_capabilities),
            "release_profile": self.release_profile,
            "release_corpus_commitment": self.release_corpus_commitment,
            "core_corpus_commitment": self.core_corpus_commitment,
            "internal_readiness": self.internal_readiness,
            "status": self.status,
            "blockers": list(self.blockers),
            "checks": [item.as_dict() for item in self.checks],
        }


def _repo_root(candidate_path: Path) -> Path:
    start = candidate_path.resolve().parent
    for parent in (start, *start.parents):
        if (parent / "conformance" / "manifest.json").is_file() and (parent / "specification").is_dir():
            return parent
    raise ValueError("could not locate OLP repository root from candidate manifest")


def _safe_path(root: Path, value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty repository-relative path")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} escapes repository root") from exc
    return candidate


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(checks: list[PromotionCheck], check_id: str, ok: bool, good: str, bad: str) -> None:
    checks.append(PromotionCheck(check_id, "PASS" if ok else "FAIL", good if ok else bad))


def _validate_candidate_shape(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("candidate manifest must be a JSON object")
    required = {
        "schema",
        "version",
        "candidate",
        "status",
        "baseline_commit",
        "baseline_release",
        "baseline_release_manifest",
        "conformance_manifest",
        "accepted_release_profile",
        "mandatory_profile",
        "mandatory_specifications",
        "optional_profiles",
        "required_artifacts",
        "external_gates",
    }
    if set(raw) != required:
        missing = sorted(required - set(raw))
        extra = sorted(set(raw) - required)
        raise ValueError(f"candidate manifest keys mismatch: missing={missing}, extra={extra}")
    if raw["schema"] != CANDIDATE_SCHEMA or raw["version"] != CANDIDATE_VERSION:
        raise ValueError("unsupported v1 promotion candidate schema/version")
    if raw["status"] != "candidate":
        raise ValueError("v1 promotion manifest status must be candidate")
    if not isinstance(raw["candidate"], str) or not raw["candidate"]:
        raise ValueError("candidate identifier must be non-empty")
    if not isinstance(raw["baseline_commit"], str) or len(raw["baseline_commit"]) != 40:
        raise ValueError("baseline_commit must be a 40-character commit id")
    if not isinstance(raw["baseline_release"], str) or not raw["baseline_release"]:
        raise ValueError("baseline_release must be non-empty")
    return raw


def _profile_registry_check(
    *,
    root: Path,
    manifest: Any,
    profiles: tuple[str, ...],
    baseline_release: str,
) -> tuple[bool, str]:
    for profile in profiles:
        try:
            capabilities = tuple(manifest.profiles[profile])
        except KeyError:
            return False, f"profile missing from executable manifest: {profile}"
        path = root / "conformance" / "profiles" / f"{profile}.json"
        if not path.is_file():
            return False, f"standalone profile missing: {profile}"
        raw = load_path(path)
        if set(raw) != {"schema", "id", "version", "status", "capabilities"}:
            return False, f"standalone profile metadata shape mismatch: {profile}"
        if raw.get("schema") != "olp-conformance-profile-v1" or raw.get("version") != 1:
            return False, f"standalone profile schema/version mismatch: {profile}"
        if raw.get("id") != profile:
            return False, f"standalone profile id mismatch: {profile}"
        if raw.get("status") != baseline_release:
            return False, f"standalone profile release status mismatch: {profile}"
        if tuple(raw.get("capabilities", ())) != capabilities:
            return False, f"standalone profile capabilities differ from executable manifest: {profile}"
    return True, "candidate standalone profiles exactly match executable profile definitions"


def _artifact_check(
    *,
    root: Path,
    name: str,
    raw: Any,
) -> tuple[bool, str, Path | None]:
    if not isinstance(raw, dict) or set(raw) != {"path", "sha256"}:
        return False, f"required artifact metadata malformed: {name}", None
    try:
        path = _safe_path(root, raw.get("path"), field=f"required_artifacts.{name}.path")
    except ValueError as exc:
        return False, str(exc), None
    expected = raw.get("sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        return False, f"required artifact SHA-256 malformed: {name}", path
    if not path.is_file():
        return False, f"required artifact missing: {name}", path
    observed = _sha256(path)
    if observed != expected:
        return False, f"required artifact digest mismatch: {name}", path
    return True, f"required artifact pinned exactly: {name}", path


def _review_register_check(
    *,
    path: Path | None,
    baseline_release: str,
    baseline_commit: str,
) -> tuple[bool, str]:
    if path is None or not path.is_file():
        return False, "review register unavailable"
    raw = load_path(path)
    required = {"schema", "version", "baseline_release", "baseline_commit", "review_scope", "findings"}
    if not isinstance(raw, dict) or set(raw) != required:
        return False, "review register metadata shape mismatch"
    if raw.get("schema") != REVIEW_SCHEMA or raw.get("version") != 1:
        return False, "review register schema/version mismatch"
    if raw.get("baseline_release") != baseline_release or raw.get("baseline_commit") != baseline_commit:
        return False, "review register baseline does not match candidate"
    scope = raw.get("review_scope")
    if not isinstance(scope, dict):
        return False, "review register scope malformed"
    expected_specs = tuple(f"{value:04d}" for value in range(16))
    if tuple(scope.get("specifications", ())) != expected_specs:
        return False, "review register must cover Specifications 0000 through 0015"
    findings = raw.get("findings")
    if not isinstance(findings, list) or not findings:
        return False, "review register must contain recorded findings"
    ids: list[str] = []
    for item in findings:
        if not isinstance(item, dict):
            return False, "review register finding is not an object"
        needed = {"id", "class", "severity", "status", "summary", "resolution"}
        if set(item) != needed:
            return False, f"review finding metadata shape mismatch: {item.get('id', '<unknown>')}"
        if item["status"] != "resolved":
            return False, f"unresolved internal review finding: {item['id']}"
        if item["class"] == "normative-contradiction" and not item["resolution"]:
            return False, f"normative contradiction lacks resolution: {item['id']}"
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        return False, "review finding ids must be unique"
    return True, "internal review register has no unresolved normative contradiction or release blocker"


def evaluate_v1_promotion(candidate_path: str | Path) -> PromotionReport:
    """Evaluate the repository's v1 candidate stable-promotion gates.

    Structural errors in the candidate document raise ``ValueError``.  Valid
    candidate documents always produce a report whose state is one of
    ``INVALID``, ``BLOCKED``, or ``READY``.
    """

    candidate_path = Path(candidate_path).resolve()
    raw = _validate_candidate_shape(load_path(candidate_path))
    root = _repo_root(candidate_path)
    checks: list[PromotionCheck] = []

    candidate_id = raw["candidate"]
    baseline_release = raw["baseline_release"]
    baseline_commit = raw["baseline_commit"]
    mandatory_profile = raw["mandatory_profile"]
    release_profile = raw["accepted_release_profile"]

    # Load the executable conformance model first; malformed global manifest
    # composition is an internal failure even if one selected profile is valid.
    try:
        manifest_path = _safe_path(root, raw["conformance_manifest"], field="conformance_manifest")
        manifest = load_manifest(manifest_path)
        checks.append(PromotionCheck("CONFORMANCE_MANIFEST", "PASS", "global conformance manifest and fragments load cleanly"))
    except Exception as exc:  # noqa: BLE001 - report release-validation failures uniformly
        manifest = None
        manifest_path = None
        checks.append(PromotionCheck("CONFORMANCE_MANIFEST", "FAIL", f"conformance manifest invalid: {exc}"))

    # Baseline release + exact Draft v0.3 corpus commitment.
    release: dict[str, Any] | None = None
    release_commitment: str | None = None
    try:
        release_path = _safe_path(root, raw["baseline_release_manifest"], field="baseline_release_manifest")
        release_raw = load_path(release_path)
        if not isinstance(release_raw, dict):
            raise ValueError("release manifest must be an object")
        release = release_raw
        release_ok = (
            release.get("schema") == "olp-specification-set-release-v1"
            and release.get("release") == baseline_release
            and release.get("interoperable_release_profile") == release_profile
        )
        _check(
            checks,
            "BASELINE_RELEASE",
            release_ok,
            "baseline release manifest matches candidate release/profile",
            "baseline release manifest does not match candidate release/profile",
        )
    except Exception as exc:  # noqa: BLE001
        checks.append(PromotionCheck("BASELINE_RELEASE", "FAIL", f"baseline release invalid: {exc}"))

    if manifest_path is not None and release is not None:
        try:
            commitment = build_profile_corpus_commitment(manifest_path, release_profile)
            release_commitment = commitment.digest_hex
            expected = release.get("conformance_suite_commitment", {}).get("digest_hex")
            accepted_caps = tuple(release.get("accepted_capabilities", ()))
            accepted_count = release.get("accepted_conformance_case_count")
            ok = (
                expected == commitment.digest_hex
                and accepted_caps == commitment.capabilities
                and accepted_count == len(commitment.case_ids)
            )
            _check(
                checks,
                "RELEASE_CORPUS_COMMITMENT",
                ok,
                f"baseline release corpus recomputes exactly: {commitment.digest_hex}",
                "baseline release corpus commitment/capability/count drift detected",
            )
        except Exception as exc:  # noqa: BLE001
            checks.append(PromotionCheck("RELEASE_CORPUS_COMMITMENT", "FAIL", f"release corpus recomputation failed: {exc}"))
    else:
        checks.append(PromotionCheck("RELEASE_CORPUS_COMMITMENT", "FAIL", "release corpus cannot be checked without valid manifest/release"))

    mandatory_caps: tuple[str, ...] = ()
    core_commitment: str | None = None
    if manifest is not None:
        mandatory_caps = tuple(manifest.profiles.get(mandatory_profile, ()))
        core_ok = mandatory_profile == "core-v1" and mandatory_caps == V1_CORE_CAPABILITIES
        _check(
            checks,
            "MANDATORY_CORE_BOUNDARY",
            core_ok,
            "mandatory candidate core is exactly the frozen eight-capability core-v1 profile",
            "mandatory candidate core is not the Specification 0015 core-v1 boundary",
        )
        if manifest_path is not None and mandatory_caps:
            try:
                core_commitment = build_profile_corpus_commitment(manifest_path, mandatory_profile).digest_hex
            except Exception as exc:  # noqa: BLE001
                checks.append(PromotionCheck("MANDATORY_CORE_CORPUS", "FAIL", f"core corpus commitment failed: {exc}"))
            else:
                checks.append(PromotionCheck("MANDATORY_CORE_CORPUS", "PASS", f"mandatory core corpus is reproducibly committed: {core_commitment}"))
    else:
        checks.append(PromotionCheck("MANDATORY_CORE_BOUNDARY", "FAIL", "mandatory core cannot be checked without manifest"))

    # Exact normative boundary declared by Specification 0015.
    mandatory_specs = tuple(raw.get("mandatory_specifications", ()))
    specs_ok = mandatory_specs == V1_MANDATORY_SPECIFICATIONS and all((root / item).is_file() for item in mandatory_specs)
    _check(
        checks,
        "MANDATORY_NORMATIVE_BOUNDARY",
        specs_ok,
        "mandatory normative specification boundary is exact and present",
        "mandatory normative specification boundary differs from Specification 0015 or contains missing files",
    )

    optional_entries = raw.get("optional_profiles")
    optional_names: tuple[str, ...] = ()
    optional_caps: tuple[str, ...] = ()
    optional_shape_ok = isinstance(optional_entries, list)
    normalized_entries: list[tuple[str, tuple[str, ...]]] = []
    if optional_shape_ok:
        for item in optional_entries:
            if not isinstance(item, dict) or set(item) != {"profile", "specifications"}:
                optional_shape_ok = False
                break
            if not isinstance(item["profile"], str) or not isinstance(item["specifications"], list):
                optional_shape_ok = False
                break
            normalized_entries.append((item["profile"], tuple(item["specifications"])))
    optional_boundary_ok = optional_shape_ok and tuple(normalized_entries) == V1_OPTIONAL_PROFILE_SPECS
    if optional_boundary_ok:
        optional_names = tuple(name for name, _ in normalized_entries)
        optional_boundary_ok = all((root / spec).is_file() for _, specs in normalized_entries for spec in specs)
    _check(
        checks,
        "OPTIONAL_PROFILE_BOUNDARY",
        optional_boundary_ok,
        "optional candidate profiles/specification associations exactly match Specification 0015",
        "optional candidate profile/specification boundary mismatch",
    )

    if manifest is not None and optional_names:
        cap_list: list[str] = []
        seen: set[str] = set(mandatory_caps)
        overlap = False
        missing = False
        for profile in optional_names:
            caps = tuple(manifest.profiles.get(profile, ()))
            if not caps:
                missing = True
                continue
            for capability in caps:
                if capability in seen:
                    overlap = True
                seen.add(capability)
                cap_list.append(capability)
        optional_caps = tuple(cap_list)
        release_caps = tuple(release.get("accepted_capabilities", ())) if release is not None else ()
        coverage = mandatory_caps + optional_caps
        coverage_ok = not overlap and not missing and coverage == release_caps
        _check(
            checks,
            "CANDIDATE_CAPABILITY_COVERAGE",
            coverage_ok,
            "mandatory plus optional candidates cover exactly the 15 Draft v0.3 accepted capabilities",
            "candidate capability coverage overlaps, omits, adds, or reorders Draft v0.3 capabilities",
        )

        registry_ok, registry_detail = _profile_registry_check(
            root=root,
            manifest=manifest,
            profiles=(mandatory_profile, *optional_names),
            baseline_release=baseline_release,
        )
        checks.append(PromotionCheck("PROFILE_REGISTRY", "PASS" if registry_ok else "FAIL", registry_detail))
    else:
        checks.append(PromotionCheck("CANDIDATE_CAPABILITY_COVERAGE", "FAIL", "candidate coverage cannot be checked"))
        checks.append(PromotionCheck("PROFILE_REGISTRY", "FAIL", "candidate profile registry cannot be checked"))

    # Required pinned stabilization artifacts. JSON object member order is not
    # semantic, so validate the exact key set and iterate in specification order.
    artifacts = raw.get("required_artifacts")
    artifact_paths: dict[str, Path | None] = {}
    if not isinstance(artifacts, dict) or set(artifacts) != set(_REQUIRED_ARTIFACT_KEYS):
        checks.append(PromotionCheck("REQUIRED_ARTIFACTS", "FAIL", "required_artifacts must contain exactly threat_model, review_register, release_process"))
    else:
        for name in _REQUIRED_ARTIFACT_KEYS:
            ok, detail, path = _artifact_check(root=root, name=name, raw=artifacts[name])
            artifact_paths[name] = path
            checks.append(PromotionCheck(f"ARTIFACT_{name.upper()}", "PASS" if ok else "FAIL", detail))

    review_ok, review_detail = _review_register_check(
        path=artifact_paths.get("review_register"),
        baseline_release=baseline_release,
        baseline_commit=baseline_commit,
    )
    checks.append(PromotionCheck("INTERNAL_REVIEW_REGISTER", "PASS" if review_ok else "FAIL", review_detail))

    # External gates are deliberately not self-satisfiable. Completed gates
    # require durable references; pending gates are valid but block promotion.
    # JSON object member order is not semantic.
    external = raw.get("external_gates")
    expected_external_names = {name for name, _ in _EXTERNAL_GATES}
    if not isinstance(external, dict) or set(external) != expected_external_names:
        checks.append(PromotionCheck("EXTERNAL_GATE_METADATA", "FAIL", "external gate set mismatch"))
    else:
        for name, blocker in _EXTERNAL_GATES:
            value = external[name]
            if not isinstance(value, dict) or set(value) != {"status", "references"}:
                checks.append(PromotionCheck(name.upper(), "FAIL", f"external gate metadata malformed: {name}"))
                continue
            gate_status = value.get("status")
            refs = value.get("references")
            if not isinstance(refs, list) or any(not isinstance(item, str) or not item for item in refs):
                checks.append(PromotionCheck(name.upper(), "FAIL", f"external gate references malformed: {name}"))
                continue
            if gate_status == "completed" and refs:
                checks.append(PromotionCheck(name.upper(), "PASS", f"external gate completed with {len(refs)} durable reference(s)"))
            elif gate_status == "pending":
                checks.append(PromotionCheck(name.upper(), "BLOCKED", f"required external gate remains pending: {name}", blocker=blocker))
            elif gate_status == "completed":
                checks.append(PromotionCheck(name.upper(), "FAIL", f"completed external gate has no durable reference: {name}"))
            else:
                checks.append(PromotionCheck(name.upper(), "FAIL", f"unsupported external gate status: {name}"))

    internal_failures = tuple(item for item in checks if item.status == "FAIL")
    blockers = tuple(item.blocker for item in checks if item.status == "BLOCKED" and item.blocker is not None)
    internal_readiness = "PASS" if not internal_failures else "FAIL"
    if internal_failures:
        state = "INVALID"
    elif blockers:
        state = "BLOCKED"
    else:
        state = "READY"

    return PromotionReport(
        candidate=candidate_id,
        baseline_release=baseline_release,
        mandatory_profile=mandatory_profile,
        mandatory_capabilities=mandatory_caps,
        optional_profiles=optional_names,
        optional_capabilities=optional_caps,
        release_profile=release_profile,
        release_corpus_commitment=release_commitment,
        core_corpus_commitment=core_commitment,
        internal_readiness=internal_readiness,
        status=state,
        blockers=blockers,
        checks=tuple(checks),
    )
