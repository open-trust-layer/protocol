"""Deterministic disclosure planning for OLP Specification 0010.

The planner selects exact immutable evidence objects and task-scoped dependency
branches.  It does not mutate records, infer global graph completeness, perform
network I/O, define a universal policy language, or implement field-level
selective-disclosure cryptography.

The normative ``DisclosureRequestV1`` is parsed exactly as Specification 0010
defines it.  ``inventory`` and dependency edges are explicit planner context,
not new OLP evidence objects or wire-level protocol types.
"""

from __future__ import annotations

import hashlib
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .encoding.proof_identity import proof_identity
from .encoding.record_identity import record_identity
from .errors import ConformanceError, UnsupportedFeatureError
from .model.bundle import ResourceRefV1
from .model.evidence import EvidenceRefV1
from .model.proof import OLPProof
from .model.record import RecordV1
from .values import is_absolute_uri, is_semantic_identifier, validate_record_value

DISCLOSURE_REQUEST_DOMAIN = "OLP-DISCLOSURE-REQUEST"
DISCLOSURE_REQUEST_VERSION = 1

CORE_PRIVACY_WARNINGS = frozenset(
    {
        "STABLE_PRINCIPAL_CORRELATION",
        "STABLE_VERIFICATION_METHOD_CORRELATION",
        "SAME_SUBJECT_LINK_DISCLOSED",
        "UNRELATED_ROLE_DISCLOSURE",
        "UNRELATED_AUTHORITY_DISCLOSURE",
        "EXCESS_LIFECYCLE_HISTORY",
        "NETWORK_RESOLUTION_LEAKAGE",
        "BUNDLE_MANIFEST_CORRELATION",
        "SELF_CONTAINED_OVERDISCLOSURE",
        "EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN",
        "GLOBAL_COMPLETENESS_NOT_ESTABLISHED",
    }
)

_DEPENDENCY_CLASSES = frozenset({"protocol", "policy", "offline"})
_TARGET_CLASSES = frozenset({"evidence", "resource"})


def _malformed(message: str, code: str = "MALFORMED_DISCLOSURE_INPUT") -> ConformanceError:
    return ConformanceError(message, code=code)


def _sort_text(values: set[str]) -> list[str]:
    return sorted(values, key=lambda item: item.encode("utf-8"))


def _ref_json(ref: EvidenceRefV1) -> dict[str, Any]:
    return {"kind": int(ref.kind), "identity_digest_hex": ref.identity_digest.hex()}


def _resource_json(ref: ResourceRefV1) -> dict[str, Any]:
    return {
        "resource_id": ref.resource_id,
        "media_type": ref.media_type,
        "hash_algorithm": ref.hash_algorithm,
        "digest_hex": ref.digest.hex(),
    }


def _evidence_key(ref: EvidenceRefV1) -> bytes:
    return ref.canonical_bytes()


def _resource_key(ref: ResourceRefV1) -> bytes:
    return ref.canonical_bytes()


@dataclass(frozen=True, slots=True)
class DisclosureRequestV1:
    purpose: str | None
    roots: tuple[EvidenceRefV1, ...]
    required_capabilities: tuple[str, ...]
    evidence_requirements: Any
    resolver_policy: Any
    options: Mapping[int, Any]
    version: int = DISCLOSURE_REQUEST_VERSION
    domain: str = DISCLOSURE_REQUEST_DOMAIN

    @classmethod
    def from_value(cls, value: Any) -> "DisclosureRequestV1":
        if not isinstance(value, (tuple, list)) or len(value) != 8:
            raise _malformed("DisclosureRequestV1 MUST be an eight-element array", "MALFORMED_DISCLOSURE_REQUEST")
        domain, version, purpose, roots_raw, capabilities_raw, requirements, resolver_policy, options = value
        if domain != DISCLOSURE_REQUEST_DOMAIN:
            raise _malformed("invalid disclosure-request discriminator", "MALFORMED_DISCLOSURE_REQUEST")
        if isinstance(version, bool) or not isinstance(version, int):
            raise _malformed("disclosure-request version MUST be integer", "MALFORMED_DISCLOSURE_REQUEST")
        if version != DISCLOSURE_REQUEST_VERSION:
            raise UnsupportedFeatureError(
                "unsupported disclosure-request version", code="UNSUPPORTED_DISCLOSURE_REQUEST_VERSION"
            )
        if purpose is not None and not is_absolute_uri(purpose):
            raise _malformed("disclosure purpose MUST be an absolute URI or null", "MALFORMED_DISCLOSURE_REQUEST")
        if not isinstance(roots_raw, (tuple, list)) or not roots_raw:
            raise _malformed("disclosure roots MUST be a non-empty array", "MALFORMED_DISCLOSURE_REQUEST")
        roots = tuple(EvidenceRefV1.from_value(item) for item in roots_raw)
        if len(set(roots)) != len(roots):
            raise _malformed("disclosure roots MUST be unique", "MALFORMED_DISCLOSURE_REQUEST")
        if not isinstance(capabilities_raw, (tuple, list)):
            raise _malformed("requiredCapabilities MUST be an array", "MALFORMED_DISCLOSURE_REQUEST")
        capabilities = tuple(capabilities_raw)
        if any(not is_semantic_identifier(item) for item in capabilities):
            raise _malformed("requiredCapabilities contains an invalid capability identifier", "MALFORMED_DISCLOSURE_REQUEST")
        if len(set(capabilities)) != len(capabilities):
            raise _malformed("requiredCapabilities MUST be a set", "MALFORMED_DISCLOSURE_REQUEST")
        if capabilities != tuple(sorted(capabilities, key=lambda item: item.encode("utf-8"))):
            raise _malformed("requiredCapabilities MUST be canonically sorted", "MALFORMED_DISCLOSURE_REQUEST")
        validate_record_value(requirements, path="DisclosureRequestV1.evidenceRequirements")
        validate_record_value(resolver_policy, path="DisclosureRequestV1.resolverPolicy")
        if not isinstance(options, Mapping):
            raise _malformed("DisclosureRequestV1 options MUST be a map", "MALFORMED_DISCLOSURE_REQUEST")
        normalized_options: dict[int, Any] = {}
        for key, option in options.items():
            if isinstance(key, bool) or not isinstance(key, int) or key not in {0, 1, 2, 3}:
                raise UnsupportedFeatureError("unsupported disclosure option", code="UNSUPPORTED_DISCLOSURE_OPTION")
            normalized_options[key] = option
        for label in (0, 1, 3):
            if label in normalized_options and not isinstance(normalized_options[label], bool):
                raise _malformed("disclosure boolean option has invalid type", "MALFORMED_DISCLOSURE_REQUEST")
        if 2 in normalized_options:
            limit = normalized_options[2]
            if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 0):
                raise _malformed("maxBundleBytes MUST be a non-negative integer or null", "MALFORMED_DISCLOSURE_REQUEST")
        return cls(
            domain=domain,
            version=version,
            purpose=purpose,
            roots=roots,
            required_capabilities=capabilities,
            evidence_requirements=requirements,
            resolver_policy=resolver_policy,
            options=normalized_options,
        )

    @property
    def prefer_minimal(self) -> bool:
        return bool(self.options.get(0, False))

    @property
    def prefer_offline(self) -> bool:
        return bool(self.options.get(1, False))

    @property
    def max_bundle_bytes(self) -> int | None:
        value = self.options.get(2)
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    @property
    def permit_external_presentations(self) -> bool:
        return bool(self.options.get(3, False))


@dataclass(frozen=True, slots=True)
class DisclosureDependency:
    target_class: str
    target: EvidenceRefV1 | ResourceRefV1
    dependency_class: str

    @classmethod
    def from_value(cls, value: Any) -> "DisclosureDependency":
        if not isinstance(value, (tuple, list)) or len(value) != 3:
            raise _malformed("disclosure dependency MUST be a three-element array")
        target_class, raw_target, dependency_class = value
        if target_class not in _TARGET_CLASSES:
            raise _malformed("unsupported disclosure dependency target class")
        if dependency_class not in _DEPENDENCY_CLASSES:
            raise _malformed("unsupported disclosure dependency class")
        target: EvidenceRefV1 | ResourceRefV1
        if target_class == "evidence":
            target = EvidenceRefV1.from_value(raw_target)
        else:
            target = ResourceRefV1.from_value(raw_target)
        return cls(target_class, target, dependency_class)

    def key(self) -> tuple[str, bytes, str]:
        encoded = self.target.canonical_bytes()
        return self.target_class, encoded, self.dependency_class

    def to_json(self) -> dict[str, Any]:
        target_json = _ref_json(self.target) if isinstance(self.target, EvidenceRefV1) else _resource_json(self.target)
        return {
            "target_class": self.target_class,
            "target": target_json,
            "dependency_class": self.dependency_class,
        }


@dataclass(slots=True)
class EvidenceInventoryItem:
    ref: EvidenceRefV1
    record: RecordV1 | None
    proof: OLPProof | None
    dependencies: tuple[DisclosureDependency, ...]
    privacy_warnings: frozenset[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "EvidenceInventoryItem":
        if "ref" not in value:
            raise _malformed("evidence inventory item is missing ref")
        ref = EvidenceRefV1.from_value(value["ref"])
        record = value.get("record")
        proof = value.get("proof")
        if record is not None and not isinstance(record, RecordV1):
            raise _malformed("evidence inventory record body was not decoded")
        if proof is not None and not isinstance(proof, OLPProof):
            raise _malformed("evidence inventory proof body was not decoded")
        if record is not None and proof is not None:
            raise _malformed("evidence inventory item cannot contain both record and proof bodies")
        if record is not None and int(ref.kind) != 0:
            raise _malformed("record body does not match EvidenceRef kind")
        if proof is not None and int(ref.kind) != 1:
            raise _malformed("proof body does not match EvidenceRef kind")
        deps_raw = value.get("dependencies", ())
        if not isinstance(deps_raw, (tuple, list)):
            raise _malformed("evidence dependencies MUST be an array")
        dependencies = tuple(DisclosureDependency.from_value(item) for item in deps_raw)
        dep_keys = tuple(dep.key() for dep in dependencies)
        if len(set(dep_keys)) != len(dep_keys):
            raise _malformed("duplicate disclosure dependency")
        warnings_raw = value.get("privacy_warnings", ())
        if not isinstance(warnings_raw, (tuple, list)):
            raise _malformed("privacy_warnings MUST be an array")
        warnings = frozenset(warnings_raw)
        if any(item not in CORE_PRIVACY_WARNINGS for item in warnings):
            raise _malformed("unknown core privacy warning in planner context")
        return cls(ref, record, proof, dependencies, warnings)

    def verify_identity(self) -> bool:
        if self.record is not None:
            return record_identity(self.record) == self.ref.identity_digest
        if self.proof is not None:
            return proof_identity(self.proof) == self.ref.identity_digest
        return True


@dataclass(slots=True)
class ResourceInventoryItem:
    ref: ResourceRefV1
    content: bytes | None
    native_presentation: bool
    privacy_warnings: frozenset[str]

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ResourceInventoryItem":
        if "ref" not in value:
            raise _malformed("resource inventory item is missing ref")
        ref = ResourceRefV1.from_value(value["ref"])
        content = value.get("content")
        if content is not None and not isinstance(content, bytes):
            raise _malformed("resource content MUST be bytes or null")
        native = value.get("native_presentation", False)
        if not isinstance(native, bool):
            raise _malformed("native_presentation MUST be boolean")
        warnings_raw = value.get("privacy_warnings", ())
        if not isinstance(warnings_raw, (tuple, list)):
            raise _malformed("resource privacy_warnings MUST be an array")
        warnings = frozenset(warnings_raw)
        if any(item not in CORE_PRIVACY_WARNINGS for item in warnings):
            raise _malformed("unknown core privacy warning in planner context")
        return cls(ref, content, native, warnings)

    def verify_identity(self) -> bool:
        if self.content is None:
            return True
        return self.ref.hash_algorithm == -16 and hashlib.sha256(self.content).digest() == self.ref.digest


def _record_privacy_warnings(record: RecordV1) -> set[str]:
    warnings: set[str] = set()
    content = record.content
    if not isinstance(content, tuple) or not content or not isinstance(content[0], str):
        return warnings
    domain = content[0]
    if domain == "OLP-PRINCIPAL-RELATION" and len(content) >= 6:
        warnings.add("STABLE_PRINCIPAL_CORRELATION")
        relation = content[2]
        if relation == "controlsVerificationMethod":
            warnings.add("STABLE_VERIFICATION_METHOD_CORRELATION")
        elif relation == "sameSubjectAs":
            warnings.add("SAME_SUBJECT_LINK_DISCLOSED")
    elif domain == "OLP-AUTHORITY-GRANT":
        warnings.add("STABLE_PRINCIPAL_CORRELATION")
    elif domain == "OLP-LIFECYCLE-STATUS" and len(content) >= 3:
        target = content[2]
        if isinstance(target, tuple) and len(target) == 2:
            if target[0] == "principal":
                warnings.add("STABLE_PRINCIPAL_CORRELATION")
            elif target[0] == "verificationMethod":
                warnings.add("STABLE_VERIFICATION_METHOD_CORRELATION")
    return warnings


def _parse_inventory(payload: Mapping[str, Any]) -> tuple[dict[EvidenceRefV1, EvidenceInventoryItem], dict[ResourceRefV1, ResourceInventoryItem]]:
    raw_evidence = payload.get("inventory", ())
    raw_resources = payload.get("resources", ())
    if not isinstance(raw_evidence, (tuple, list)) or not isinstance(raw_resources, (tuple, list)):
        raise _malformed("planner inventory/resources MUST be arrays")
    evidence: dict[EvidenceRefV1, EvidenceInventoryItem] = {}
    for raw in raw_evidence:
        if not isinstance(raw, Mapping):
            raise _malformed("evidence inventory entries MUST be maps")
        item = EvidenceInventoryItem.from_mapping(raw)
        if item.ref in evidence:
            raise _malformed("duplicate evidence inventory reference")
        evidence[item.ref] = item
    resources: dict[ResourceRefV1, ResourceInventoryItem] = {}
    for raw in raw_resources:
        if not isinstance(raw, Mapping):
            raise _malformed("resource inventory entries MUST be maps")
        item = ResourceInventoryItem.from_mapping(raw)
        if item.ref in resources:
            raise _malformed("duplicate resource inventory reference")
        resources[item.ref] = item
    return evidence, resources


def _status_for(errors: set[str], unresolved: list[DisclosureDependency], policy_blocked: bool) -> str:
    if policy_blocked:
        return "POLICY_BLOCKED"
    if "REQUIRED_CAPABILITY_UNAVAILABLE" in errors:
        return "UNSUPPORTED"
    if errors & {"ROOT_NOT_AVAILABLE", "EVIDENCE_IDENTITY_MISMATCH", "RESOURCE_DIGEST_MISMATCH"}:
        return "UNSATISFIABLE"
    if unresolved:
        return "PARTIAL"
    return "READY"


def plan_disclosure(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Plan task-scoped minimized disclosure without performing external I/O.

    ``payload`` contains the normative ``request`` plus explicit planner context:
    ``inventory``, ``resources``, optional ``available_capabilities``, and two
    privacy observability flags (``manifested`` and ``network_resolution_planned``).
    """

    if not isinstance(payload, Mapping):
        raise _malformed("disclosure planner input MUST be a map")
    if "request" not in payload:
        raise _malformed("disclosure planner input is missing request")
    request = DisclosureRequestV1.from_value(payload["request"])
    evidence, resources = _parse_inventory(payload)

    available_raw = payload.get("available_capabilities")
    available: frozenset[str] | None = None
    if available_raw is not None:
        if not isinstance(available_raw, (tuple, list)) or any(not is_semantic_identifier(v) for v in available_raw):
            raise _malformed("available_capabilities MUST be an array of capability identifiers")
        available = frozenset(available_raw)

    manifested = payload.get("manifested", True)
    network_planned = payload.get("network_resolution_planned", False)
    if not isinstance(manifested, bool) or not isinstance(network_planned, bool):
        raise _malformed("planner privacy observability flags MUST be boolean")

    errors: set[str] = set()
    privacy_warnings: set[str] = {"GLOBAL_COMPLETENESS_NOT_ESTABLISHED"}
    policy_warnings: set[str] = set()
    if manifested:
        privacy_warnings.add("BUNDLE_MANIFEST_CORRELATION")
    if network_planned:
        privacy_warnings.add("NETWORK_RESOLUTION_LEAKAGE")
    if request.max_bundle_bytes is not None:
        # Specification 0008 packaging determines final bundle framing/manifest
        # size.  The pure planner cannot safely claim that a plan is within the
        # byte limit before packaging, so it exposes the deferred check.
        policy_warnings.add("MAX_BUNDLE_BYTES_REQUIRES_PACKAGING_CHECK")
    if available is not None:
        missing_caps = set(request.required_capabilities) - set(available)
        if missing_caps:
            errors.add("REQUIRED_CAPABILITY_UNAVAILABLE")

    selected: dict[EvidenceRefV1, EvidenceInventoryItem] = {}
    selected_resources: dict[ResourceRefV1, ResourceInventoryItem] = {}
    unresolved: dict[tuple[str, bytes, str], DisclosureDependency] = {}
    policy_blocked = False
    offline_support_selected = False

    queue: deque[EvidenceRefV1] = deque(request.roots)
    requested_roots = set(request.roots)
    while queue:
        ref = queue.popleft()
        if ref in selected:
            continue
        item = evidence.get(ref)
        if item is None:
            dependency = DisclosureDependency("evidence", ref, "protocol")
            unresolved[dependency.key()] = dependency
            if ref in requested_roots:
                errors.add("ROOT_NOT_AVAILABLE")
            continue
        if not item.verify_identity():
            errors.add("EVIDENCE_IDENTITY_MISMATCH")
            continue
        selected[ref] = item
        privacy_warnings.update(item.privacy_warnings)
        if item.record is not None:
            privacy_warnings.update(_record_privacy_warnings(item.record))
        if item.proof is not None:
            privacy_warnings.add("STABLE_VERIFICATION_METHOD_CORRELATION")

        for dependency in sorted(item.dependencies, key=DisclosureDependency.key):
            if dependency.dependency_class == "offline" and not request.prefer_offline:
                continue
            if dependency.dependency_class == "offline":
                offline_support_selected = True
            if dependency.target_class == "evidence":
                target = dependency.target
                assert isinstance(target, EvidenceRefV1)
                if target not in evidence:
                    unresolved[dependency.key()] = dependency
                else:
                    queue.append(target)
                continue

            target = dependency.target
            assert isinstance(target, ResourceRefV1)
            resource = resources.get(target)
            if resource is None:
                unresolved[dependency.key()] = dependency
                continue
            if resource.native_presentation and not request.permit_external_presentations:
                policy_blocked = True
                errors.add("EXTERNAL_NATIVE_PRESENTATION_NOT_PERMITTED")
                continue
            if not resource.verify_identity():
                errors.add("RESOURCE_DIGEST_MISMATCH")
                continue
            selected_resources[target] = resource
            privacy_warnings.update(resource.privacy_warnings)
            if resource.native_presentation:
                privacy_warnings.add("EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN")

    if offline_support_selected:
        privacy_warnings.add("SELF_CONTAINED_OVERDISCLOSURE")

    selected_refs = sorted(selected, key=_evidence_key)
    selected_resource_refs = sorted(selected_resources, key=_resource_key)
    selected_roots = sorted((ref for ref in request.roots if ref in selected), key=_evidence_key)
    unresolved_items = [unresolved[key] for key in sorted(unresolved)]
    status = _status_for(errors, unresolved_items, policy_blocked)

    return {
        "status": status,
        "purpose": request.purpose,
        "selected_roots": [_ref_json(ref) for ref in selected_roots],
        "selected_evidence": [_ref_json(ref) for ref in selected_refs],
        "selected_resources": [_resource_json(ref) for ref in selected_resource_refs],
        "unresolved_dependencies": [item.to_json() for item in unresolved_items],
        "privacy_warnings": _sort_text(privacy_warnings),
        "policy_warnings": _sort_text(policy_warnings),
        "produced_bundle_id": None,
        "errors": _sort_text(errors),
        "disclosure_claim": "TASK_SCOPED_MINIMIZED_DISCLOSURE",
        "global_completeness_established": False,
        "field_redaction_performed": False,
    }
