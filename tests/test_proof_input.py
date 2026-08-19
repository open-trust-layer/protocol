from __future__ import annotations

from dataclasses import replace

import pytest

from conftest import TEST_METHOD, load_vector
from olp.encoding.proof_input import build_proof_input, encode_proof_input, proof_input_bytes
from olp.errors import ConformanceError
from olp.model.proof import OLPProof, RecordCommitment


def test_specification_0004_proof_input_vector_exact_bytes():
    vector = load_vector("0004-proof-input-v1.json")
    commitment = RecordCommitment(
        vector["record_commitment"]["algorithm"],
        bytes.fromhex(vector["record_commitment"]["digest_hex"]),
    )
    proof_input = build_proof_input(
        cryptosuite=vector["cryptosuite"],
        proof_purpose=vector["proof_purpose"],
        verification_method=vector["verification_method"],
        record_commitment=commitment,
    )
    encoded = encode_proof_input(proof_input)
    assert len(proof_input) == 9
    assert len(encoded) == vector["expected"]["proof_input_length"]
    assert encoded.hex() == vector["expected"]["proof_input_hex"]


def test_metadata_uses_integer_labels_and_exact_values(sample_proof):
    proof = replace(
        sample_proof,
        created="2026-08-20T00:00:00Z",
        expires="2026-08-21T00:00:00+00:00",
        domain="example.org",
        challenge=b"challenge",
        nonce=b"nonce",
    )
    value = build_proof_input(
        cryptosuite=proof.cryptosuite,
        proof_purpose=proof.proofPurpose,
        verification_method=proof.verificationMethod,
        record_commitment=proof.recordCommitment,
        created=proof.created,
        expires=proof.expires,
        domain=proof.domain,
        challenge=proof.challenge,
        nonce=proof.nonce,
    )
    metadata = value[6]
    assert metadata == {
        0: "2026-08-20T00:00:00Z",
        1: "2026-08-21T00:00:00+00:00",
        2: "example.org",
        3: b"challenge",
        4: b"nonce",
    }


def test_critical_is_sorted_by_utf8_bytes(sample_proof):
    extensions = {
        "https://example.org/z": 1,
        "https://example.org/a": 2,
    }
    value = build_proof_input(
        cryptosuite=sample_proof.cryptosuite,
        proof_purpose=sample_proof.proofPurpose,
        verification_method=sample_proof.verificationMethod,
        record_commitment=sample_proof.recordCommitment,
        extensions=extensions,
        critical=("https://example.org/z", "https://example.org/a"),
    )
    assert value[8] == ("https://example.org/a", "https://example.org/z")


def test_extension_map_insertion_order_does_not_change_bytes(sample_proof):
    kwargs = dict(
        cryptosuite=sample_proof.cryptosuite,
        proof_purpose=sample_proof.proofPurpose,
        verification_method=sample_proof.verificationMethod,
        record_commitment=sample_proof.recordCommitment,
    )
    a = build_proof_input(**kwargs, extensions={"https://example.org/b": 2, "https://example.org/a": 1})
    b = build_proof_input(**kwargs, extensions={"https://example.org/a": 1, "https://example.org/b": 2})
    assert encode_proof_input(a) == encode_proof_input(b)


def test_proof_value_is_not_in_proof_input(sample_proof):
    changed = replace(sample_proof, proofValue=b"\xff" * 64)
    assert proof_input_bytes(sample_proof) == proof_input_bytes(changed)


@pytest.mark.parametrize(
    "field,value",
    [
        ("proofPurpose", "witness"),
        ("verificationMethod", "urn:example:olp:other-key"),
        ("cryptosuite", "https://example.org/suite/v2"),
        ("domain", "different.example"),
        ("challenge", b"different"),
        ("nonce", b"different"),
    ],
)
def test_authenticated_field_mutation_changes_proof_input(sample_proof, field, value):
    changed = replace(sample_proof, **{field: value})
    # Unknown suites remain structurally valid, so the Proof Input can still be reconstructed.
    assert proof_input_bytes(sample_proof) != proof_input_bytes(changed)


def test_record_commitment_mutation_changes_proof_input(sample_proof):
    changed = replace(
        sample_proof,
        recordCommitment=RecordCommitment(sample_proof.recordCommitment.algorithm, b"\x11" * 32),
    )
    assert proof_input_bytes(sample_proof) != proof_input_bytes(changed)


def test_invalid_critical_declaration_rejected(sample_proof):
    proof = replace(sample_proof, critical=("https://example.org/missing",))
    with pytest.raises(ConformanceError) as exc:
        proof_input_bytes(proof)
    assert exc.value.code == "INVALID_CRITICAL_DECLARATION"


def test_invalid_extension_name_rejected(sample_proof):
    proof = replace(sample_proof, extensions={"not-absolute": True})
    with pytest.raises(ConformanceError) as exc:
        proof_input_bytes(proof)
    assert exc.value.code == "INVALID_EXTENSION_NAME"


def test_proof_input_integer_extension_range_is_restricted(sample_proof):
    proof = replace(sample_proof, extensions={"https://example.org/int": 1 << 63})
    with pytest.raises(ConformanceError):
        proof_input_bytes(proof)


def test_verification_method_text_is_not_normalized(sample_proof):
    changed = replace(sample_proof, verificationMethod=TEST_METHOD.upper())
    assert proof_input_bytes(sample_proof) != proof_input_bytes(changed)
