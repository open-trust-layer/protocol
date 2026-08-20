"""Specification 0008 deterministic manifested-bundle processing core."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from .encoding.proof_identity import proof_identity
from .encoding.record_identity import record_identity
from .errors import ConformanceError, ResourceLimitError
from .model.bundle import BundleManifestStatementV1, ResourceRefV1
from .model.evidence import EvidenceKind, EvidenceRefV1
from .model.proof import OLPProof
from .model.record import RecordV1

@dataclass(frozen=True, slots=True)
class PackagedResourceV1:
    ref: ResourceRefV1
    content: bytes

@dataclass(frozen=True, slots=True)
class BundleLimits:
    max_records: int = 10_000
    max_proofs: int = 10_000
    max_resources: int = 1_000
    max_resource_bytes: int = 16 * 1024 * 1024


def parse_bundle_manifest(record: RecordV1, *, understood_critical_extensions: frozenset[str] = frozenset()) -> BundleManifestStatementV1:
    record.validate()
    statement = BundleManifestStatementV1.from_value(record.content)
    statement.validate(understood_critical_extensions=understood_critical_extensions)
    return statement


def record_ref(record: RecordV1) -> EvidenceRefV1:
    return EvidenceRefV1(EvidenceKind.RECORD, record_identity(record))


def proof_ref(proof: OLPProof) -> EvidenceRefV1:
    return EvidenceRefV1(EvidenceKind.PROOF, proof_identity(proof))


def process_bundle(
    manifest_record: RecordV1,
    *,
    records: Iterable[RecordV1] = (),
    proofs: Iterable[OLPProof] = (),
    resources: Iterable[PackagedResourceV1] = (),
    understood_critical_extensions: frozenset[str] = frozenset(),
    limits: BundleLimits = BundleLimits(),
) -> dict[str, object]:
    statement = parse_bundle_manifest(manifest_record, understood_critical_extensions=understood_critical_extensions)
    records = tuple(records); proofs = tuple(proofs); resources = tuple(resources)
    if len(records) > limits.max_records or len(proofs) > limits.max_proofs or len(resources) > limits.max_resources:
        raise ResourceLimitError("bundle object count exceeds implementation limit")

    supplied: dict[EvidenceRefV1, object] = {}
    duplicate_supplied: list[str] = []
    for item, ref in [(r, record_ref(r)) for r in records] + [(p, proof_ref(p)) for p in proofs]:
        if ref in supplied:
            duplicate_supplied.append(ref.identity_digest.hex())
        else:
            supplied[ref] = item

    manifest_inventory = set(statement.inventory)
    supplied_set = set(supplied)
    missing = sorted(manifest_inventory - supplied_set, key=lambda r: r.canonical_bytes())
    unexpected = sorted(supplied_set - manifest_inventory, key=lambda r: r.canonical_bytes())

    resource_expected = {r.canonical_bytes(): r for r in statement.resource_inventory}
    resource_seen: dict[bytes, PackagedResourceV1] = {}
    resource_errors: list[dict[str, str]] = []
    for packaged in resources:
        packaged.ref.validate()
        if len(packaged.content) > limits.max_resource_bytes:
            raise ResourceLimitError("packaged resource exceeds implementation limit")
        digest = hashlib.sha256(packaged.content).digest()
        if digest != packaged.ref.digest:
            resource_errors.append({"reason": "RESOURCE_DIGEST_MISMATCH", "resource_digest_hex": packaged.ref.digest.hex()})
        key = packaged.ref.canonical_bytes()
        if key in resource_seen:
            resource_errors.append({"reason": "DUPLICATE_PACKAGED_RESOURCE", "resource_digest_hex": packaged.ref.digest.hex()})
        else:
            resource_seen[key] = packaged
    missing_resources = [resource_expected[k] for k in sorted(set(resource_expected) - set(resource_seen))]
    unexpected_resources = [resource_seen[k].ref for k in sorted(set(resource_seen) - set(resource_expected))]

    root_results = []
    for root in statement.roots:
        root_results.append({"ref": _ref_json(root), "present": root in supplied})

    status = "VALID"
    if missing or unexpected or missing_resources or unexpected_resources or duplicate_supplied:
        status = "PARTIAL"
    if resource_errors:
        status = "INVALID"

    return {
        "status": status,
        "bundle_id_hex": record_identity(manifest_record).hex(),
        "profile": statement.profile,
        "network_fallback_allowed": statement.profile != "selfContainedVerification",
        "root_results": root_results,
        "missing_items": [_ref_json(r) for r in missing],
        "unexpected_items": [_ref_json(r) for r in unexpected],
        "duplicate_supplied_identity_hex": sorted(duplicate_supplied),
        "missing_resources": [_resource_json(r) for r in missing_resources],
        "unexpected_resources": [_resource_json(r) for r in unexpected_resources],
        "resource_errors": resource_errors,
        "closure_status": "COMPLETE" if status == "VALID" else "INCOMPLETE",
    }


def _ref_json(ref: EvidenceRefV1) -> dict[str, object]:
    return {"kind": int(ref.kind), "identity_digest_hex": ref.identity_digest.hex()}


def _resource_json(ref: ResourceRefV1) -> dict[str, object]:
    return {"resource_id": ref.resource_id, "media_type": ref.media_type, "hash_algorithm": ref.hash_algorithm, "digest_hex": ref.digest.hex()}
