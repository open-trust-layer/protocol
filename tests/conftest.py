from __future__ import annotations

import json
from pathlib import Path

import pytest

from olp.crypto.ed25519 import public_key_bytes
from olp.crypto.proof import create_proof
from olp.model.record import RecordV1
from olp.model.verification import ResolvedVerificationMethod

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "vectors"

TEST_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
TEST_METHOD = "urn:example:olp:test-key-1"


def load_vector(name: str) -> dict:
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


@pytest.fixture
def sample_record() -> RecordV1:
    return RecordV1(
        envelope_version=1,
        type="claim",
        content={"subject": "urn:example:subject:1", "statement": "example"},
    )


@pytest.fixture
def test_seed() -> bytes:
    return TEST_SEED


@pytest.fixture
def resolved_method(test_seed: bytes) -> ResolvedVerificationMethod:
    return ResolvedVerificationMethod(
        identifier=TEST_METHOD,
        key_type="Ed25519",
        public_key=public_key_bytes(test_seed),
    )


@pytest.fixture
def sample_proof(sample_record: RecordV1, test_seed: bytes):
    return create_proof(
        sample_record,
        proof_purpose="assertion",
        verification_method=TEST_METHOD,
        private_key=test_seed,
    )
