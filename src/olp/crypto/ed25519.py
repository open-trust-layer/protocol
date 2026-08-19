"""Mandatory Pure Ed25519 suite primitive wrappers.

The wrapper accepts raw 32-byte RFC 8032 seed/public-key material and exposes
only the operations needed by the OLP mandatory v1 cryptosuite.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from ..errors import KeyMaterialError

PRIVATE_SEED_LENGTH = 32
PUBLIC_KEY_LENGTH = 32
SIGNATURE_LENGTH = 64


def private_key_from_seed(seed: bytes) -> Ed25519PrivateKey:
    if not isinstance(seed, bytes) or len(seed) != PRIVATE_SEED_LENGTH:
        raise KeyMaterialError("Ed25519 private seed MUST contain exactly 32 octets")
    return Ed25519PrivateKey.from_private_bytes(seed)


def public_key_from_bytes(public_key: bytes) -> Ed25519PublicKey:
    if not isinstance(public_key, bytes) or len(public_key) != PUBLIC_KEY_LENGTH:
        raise KeyMaterialError("Ed25519 public key MUST contain exactly 32 octets")
    return Ed25519PublicKey.from_public_bytes(public_key)


def public_key_bytes(private_key_or_seed: Ed25519PrivateKey | bytes) -> bytes:
    private_key = (
        private_key_from_seed(private_key_or_seed)
        if isinstance(private_key_or_seed, bytes)
        else private_key_or_seed
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise KeyMaterialError("expected Ed25519 private key or 32-byte seed")
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def sign(private_key_or_seed: Ed25519PrivateKey | bytes, message: bytes) -> bytes:
    private_key = (
        private_key_from_seed(private_key_or_seed)
        if isinstance(private_key_or_seed, bytes)
        else private_key_or_seed
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise KeyMaterialError("expected Ed25519 private key or 32-byte seed")
    signature = private_key.sign(message)
    if len(signature) != SIGNATURE_LENGTH:
        raise KeyMaterialError("Ed25519 implementation returned an unexpected signature length")
    return signature


def verify(public_key: bytes, signature: bytes, message: bytes) -> bool:
    if not isinstance(signature, bytes) or len(signature) != SIGNATURE_LENGTH:
        raise KeyMaterialError("Ed25519 signature MUST contain exactly 64 octets")
    key = public_key_from_bytes(public_key)
    try:
        key.verify(signature, message)
    except InvalidSignature:
        return False
    return True
