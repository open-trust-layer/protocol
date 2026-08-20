from __future__ import annotations

import hashlib

import pytest

from olp.disclosure import plan_disclosure
from olp.encoding.record_identity import record_identity
from olp.errors import ConformanceError, UnsupportedFeatureError
from olp.model.bundle import ResourceRefV1
from olp.model.evidence import EvidenceRefV1
from olp.model.record import RecordV1


KNOWN_RECORD = RecordV1(
    envelope_version=1,
    type="claim",
    content={"statement": "example", "subject": "urn:example:subject:1"},
)
KNOWN_RECORD_DIGEST = bytes.fromhex(
    "c69ed0f4c22fc0242da939d45448ec1fab7464fa054af334927dc0f91741cbb4"
)


def ref(byte: int, *, kind: int = 0) -> EvidenceRefV1:
    return EvidenceRefV1(kind, bytes([byte]) * 32)


def request(
    roots,
    *,
    options=None,
    required_capabilities=(),
    version=1,
    purpose="urn:example:purpose:verify",
):
    return [
        "OLP-DISCLOSURE-REQUEST",
        version,
        purpose,
        [item.to_value() for item in roots],
        list(required_capabilities),
        {},
        {},
        options or {},
    ]


def item(reference, *, record=None, dependencies=(), privacy_warnings=()):
    return {
        "ref": reference.to_value(),
        "record": record,
        "dependencies": list(dependencies),
        "privacy_warnings": list(privacy_warnings),
    }


def test_whole_object_minimization_omits_unrelated_sibling():
    root = EvidenceRefV1(0, KNOWN_RECORD_DIGEST)
    sibling = ref(0x22)
    result = plan_disclosure(
        {
            "request": request([root], options={0: True}),
            "inventory": [item(root, record=KNOWN_RECORD), item(sibling)],
            "manifested": False,
        }
    )
    assert result["status"] == "READY"
    assert [entry["identity_digest_hex"] for entry in result["selected_evidence"]] == [KNOWN_RECORD_DIGEST.hex()]
    assert result["global_completeness_established"] is False
    assert result["field_redaction_performed"] is False
    assert "GLOBAL_COMPLETENESS_NOT_ESTABLISHED" in result["privacy_warnings"]


def test_graph_subset_follows_only_explicit_required_branch():
    a, b, c = ref(0x11), ref(0x22), ref(0x33)
    dep_b = ["evidence", b.to_value(), "protocol"]
    result = plan_disclosure(
        {
            "request": request([a]),
            "inventory": [item(a, dependencies=[dep_b]), item(b), item(c)],
            "manifested": False,
        }
    )
    selected = {entry["identity_digest_hex"] for entry in result["selected_evidence"]}
    assert selected == {a.identity_digest.hex(), b.identity_digest.hex()}
    assert c.identity_digest.hex() not in selected


def test_unresolved_required_dependency_is_explicit_and_partial():
    a, missing = ref(0x11), ref(0x44)
    result = plan_disclosure(
        {
            "request": request([a]),
            "inventory": [item(a, dependencies=[["evidence", missing.to_value(), "policy"]])],
            "manifested": False,
        }
    )
    assert result["status"] == "PARTIAL"
    assert result["unresolved_dependencies"] == [
        {
            "target_class": "evidence",
            "target": {"kind": 0, "identity_digest_hex": missing.identity_digest.hex()},
            "dependency_class": "policy",
        }
    ]


def test_field_deleted_or_modified_record_cannot_retain_original_identity():
    root = EvidenceRefV1(0, KNOWN_RECORD_DIGEST)
    altered = RecordV1(
        envelope_version=1,
        type="claim",
        content={"subject": "urn:example:subject:1"},
    )
    assert record_identity(altered) != KNOWN_RECORD_DIGEST
    result = plan_disclosure(
        {"request": request([root]), "inventory": [item(root, record=altered)], "manifested": False}
    )
    assert result["status"] == "UNSATISFIABLE"
    assert result["selected_evidence"] == []
    assert result["errors"] == ["EVIDENCE_IDENTITY_MISMATCH"]
    assert result["field_redaction_performed"] is False


def test_offline_dependency_is_selected_only_when_requested():
    root = ref(0x11)
    content = b"verification-method-document"
    resource = ResourceRefV1(None, "application/json", -16, hashlib.sha256(content).digest())
    dependency = ["resource", resource.to_value(), "offline"]
    inventory = [item(root, dependencies=[dependency])]
    resources = [{"ref": resource.to_value(), "content": content}]

    online = plan_disclosure(
        {"request": request([root]), "inventory": inventory, "resources": resources, "manifested": False}
    )
    assert online["selected_resources"] == []

    offline = plan_disclosure(
        {
            "request": request([root], options={1: True}),
            "inventory": inventory,
            "resources": resources,
            "manifested": False,
        }
    )
    assert len(offline["selected_resources"]) == 1
    assert "SELF_CONTAINED_OVERDISCLOSURE" in offline["privacy_warnings"]


def test_same_subject_relation_emits_correlation_warning():
    relation_record = RecordV1(
        envelope_version=1,
        type="principal.relation",
        content=[
            "OLP-PRINCIPAL-RELATION",
            1,
            "sameSubjectAs",
            "did:example:pairwise-a",
            [0, "did:example:pairwise-b"],
            None,
            {},
            [],
        ],
    )
    relation_ref = EvidenceRefV1(0, record_identity(relation_record))
    result = plan_disclosure(
        {
            "request": request([relation_ref]),
            "inventory": [item(relation_ref, record=relation_record)],
            "manifested": False,
        }
    )
    assert "STABLE_PRINCIPAL_CORRELATION" in result["privacy_warnings"]
    assert "SAME_SUBJECT_LINK_DISCLOSED" in result["privacy_warnings"]


def test_external_native_presentation_is_policy_blocked_unless_permitted():
    root = ref(0x11)
    content = b"native-selective-disclosure-presentation"
    resource = ResourceRefV1(None, "application/sd-jwt", -16, hashlib.sha256(content).digest())
    dependency = ["resource", resource.to_value(), "protocol"]
    inventory = [item(root, dependencies=[dependency])]
    resources = [{"ref": resource.to_value(), "content": content, "native_presentation": True}]

    blocked = plan_disclosure(
        {"request": request([root]), "inventory": inventory, "resources": resources, "manifested": False}
    )
    assert blocked["status"] == "POLICY_BLOCKED"
    assert "EXTERNAL_NATIVE_PRESENTATION_NOT_PERMITTED" in blocked["errors"]

    allowed = plan_disclosure(
        {
            "request": request([root], options={3: True}),
            "inventory": inventory,
            "resources": resources,
            "manifested": False,
        }
    )
    assert allowed["status"] == "READY"
    assert "EXTERNAL_PRESENTATION_UNLINKABILITY_UNKNOWN" in allowed["privacy_warnings"]


def test_required_capability_unavailable_is_structured_unsupported():
    root = ref(0x11)
    result = plan_disclosure(
        {
            "request": request([root], required_capabilities=("olp.proof-verification.v1",)),
            "inventory": [item(root)],
            "available_capabilities": ["olp.record-identity.v1"],
            "manifested": False,
        }
    )
    assert result["status"] == "UNSUPPORTED"
    assert result["errors"] == ["REQUIRED_CAPABILITY_UNAVAILABLE"]


def test_max_bundle_bytes_is_deferred_to_exact_packaging_check():
    root = ref(0x11)
    result = plan_disclosure(
        {
            "request": request([root], options={2: 100}),
            "inventory": [item(root)],
            "manifested": False,
        }
    )
    assert result["status"] == "READY"
    assert result["policy_warnings"] == ["MAX_BUNDLE_BYTES_REQUIRES_PACKAGING_CHECK"]


def test_request_version_and_sorted_capabilities_fail_closed():
    root = ref(0x11)
    with pytest.raises(UnsupportedFeatureError) as exc:
        plan_disclosure({"request": request([root], version=2), "inventory": [item(root)]})
    assert exc.value.code == "UNSUPPORTED_DISCLOSURE_REQUEST_VERSION"

    with pytest.raises(ConformanceError) as exc:
        plan_disclosure(
            {
                "request": request(
                    [root],
                    required_capabilities=("olp.proof-verification.v1", "olp.bundle.v1"),
                ),
                "inventory": [item(root)],
            }
        )
    assert exc.value.code == "MALFORMED_DISCLOSURE_REQUEST"
