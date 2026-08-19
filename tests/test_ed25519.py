from __future__ import annotations

import pytest

from conftest import load_vector
from olp.crypto.ed25519 import public_key_bytes, sign, verify
from olp.encoding.proof_input import build_proof_input, encode_proof_input
from olp.errors import KeyMaterialError
from olp.model.proof import RecordCommitment


def _vector_message_and_key():
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
    return vector, encode_proof_input(proof_input)


def test_specification_vector_public_key_and_signature():
    vector, message = _vector_message_and_key()
    expected = vector["expected"]
    seed = bytes.fromhex(expected["private_seed_hex"])
    assert public_key_bytes(seed).hex() == expected["public_key_hex"]
    assert sign(seed, message).hex() == expected["proof_value_hex"]
    assert verify(bytes.fromhex(expected["public_key_hex"]), bytes.fromhex(expected["proof_value_hex"]), message)


def test_signature_is_deterministic():
    vector, message = _vector_message_and_key()
    seed = bytes.fromhex(vector["expected"]["private_seed_hex"])
    assert sign(seed, message) == sign(seed, message)


def test_changed_message_does_not_verify():
    vector, message = _vector_message_and_key()
    expected = vector["expected"]
    assert not verify(
        bytes.fromhex(expected["public_key_hex"]),
        bytes.fromhex(expected["proof_value_hex"]),
        message + b"x",
    )


def test_private_seed_length_is_strict():
    with pytest.raises(KeyMaterialError):
        sign(b"short", b"message")


def test_public_key_length_is_strict():
    with pytest.raises(KeyMaterialError):
        verify(b"short", b"\x00" * 64, b"message")


def test_signature_length_is_strict():
    with pytest.raises(KeyMaterialError):
        verify(b"\x00" * 32, b"short", b"message")
