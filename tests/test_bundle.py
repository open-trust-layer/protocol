from __future__ import annotations

import hashlib
import pytest

from olp.bundle import PackagedResourceV1, process_bundle
from olp.encoding.record_identity import record_identity
from olp.errors import ConformanceError, UnsupportedFeatureError
from olp.model.bundle import BundleManifestStatementV1, ResourceRefV1
from olp.model.evidence import EvidenceKind, EvidenceRefV1
from olp.model.record import RecordV1


def claim() -> RecordV1:
    return RecordV1(1, "claim", {"subject": "urn:example:subject:1", "statement": "example"})


def manifest_for(record: RecordV1, *, profile="portable", extensions=None, critical=()) -> RecordV1:
    ref = EvidenceRefV1(EvidenceKind.RECORD, record_identity(record))
    statement = BundleManifestStatementV1(profile, (ref,), (ref,), extensions=extensions or {}, critical=critical)
    statement.validate(understood_critical_extensions=frozenset(critical))
    return RecordV1(1, "bundle-manifest", statement.to_value())


def test_bundle_valid_and_identity_stable():
    rec = claim(); manifest = manifest_for(rec)
    out = process_bundle(manifest, records=[rec])
    assert out["status"] == "VALID"
    assert out["bundle_id_hex"] == record_identity(manifest).hex()
    assert out["closure_status"] == "COMPLETE"


def test_bundle_missing_inventory_member_is_partial_not_invalid():
    rec = claim(); manifest = manifest_for(rec)
    out = process_bundle(manifest)
    assert out["status"] == "PARTIAL"
    assert len(out["missing_items"]) == 1


def test_self_contained_profile_forbids_network_fallback():
    rec = claim(); manifest = manifest_for(rec, profile="selfContainedVerification")
    out = process_bundle(manifest, records=[rec])
    assert out["network_fallback_allowed"] is False


def test_resource_digest_mismatch_is_structured_invalid():
    rec = claim(); ref = EvidenceRefV1(EvidenceKind.RECORD, record_identity(rec))
    rr = ResourceRefV1("https://example.org/key", "application/octet-stream", -16, hashlib.sha256(b"good").digest())
    s = BundleManifestStatementV1("portable", (ref,), (ref,), (rr,)); s.validate()
    m = RecordV1(1, "bundle-manifest", s.to_value())
    out = process_bundle(m, records=[rec], resources=[PackagedResourceV1(rr, b"bad")])
    assert out["status"] == "INVALID"
    assert out["resource_errors"][0]["reason"] == "RESOURCE_DIGEST_MISMATCH"


def test_manifest_inventory_requires_canonical_order():
    a = EvidenceRefV1(0, b"\x02" * 32); b = EvidenceRefV1(0, b"\x01" * 32)
    s = BundleManifestStatementV1("portable", (), (a, b))
    with pytest.raises(ConformanceError) as exc:
        s.validate()
    assert exc.value.code == "NON_CANONICAL_BUNDLE_INVENTORY_ORDER"


def test_unknown_critical_extension_fails_closed():
    rec = claim(); ext = "https://example.org/ext/critical"; m = manifest_for(rec, extensions={ext: True}, critical=(ext,))
    with pytest.raises(UnsupportedFeatureError) as exc:
        process_bundle(m, records=[rec])
    assert exc.value.code == "UNSUPPORTED_CRITICAL_BUNDLE_EXTENSION"
