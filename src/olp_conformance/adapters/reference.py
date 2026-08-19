"""Adapter for the Python OLP reference implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from olp.constants import MANDATORY_CRYPTOSUITE
from olp.crypto.commitments import record_commitment
from olp.crypto.proof import create_proof, verify_proof
from olp.encoding.proof_input import build_proof_input, encode_proof_input, proof_input_bytes
from olp.encoding.record_identity import record_identity, record_identity_bytes, record_identity_text
from olp.errors import ConformanceError, KeyMaterialError, UnsupportedFeatureError
from olp.model.proof import RecordCommitment
from olp.model.verification import MethodStatus

from ..adapter import AdapterExecutionError
from ..codec import (
    commitment_to_json,
    decode_value,
    policy_from_json,
    proof_from_json,
    proof_to_json,
    record_from_json,
    resolved_method_from_json,
    result_to_json,
)

CAPABILITIES = frozenset(
    {
        "olp.record-identity.v1",
        "olp.record-commitment.sha256.v1",
        "olp.proof-input.v1",
        "olp.proof.eddsa-ed25519.v1",
        "olp.proof-verification.v1",
    }
)


class ReferenceAdapter:
    @property
    def name(self) -> str:
        return "python-reference"

    def capabilities(self) -> frozenset[str]:
        return CAPABILITIES

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return getattr(self, f"_op_{operation}")(payload)
        except AdapterExecutionError:
            raise
        except UnsupportedFeatureError as exc:
            raise AdapterExecutionError("UNSUPPORTED", exc.code or "UNSUPPORTED", str(exc)) from exc
        except (ConformanceError, KeyMaterialError, ValueError, TypeError, KeyError) as exc:
            reason = getattr(exc, "code", None) or "MALFORMED_INPUT"
            raise AdapterExecutionError("MALFORMED", str(reason), str(exc)) from exc
        except AttributeError as exc:
            raise AdapterExecutionError("UNSUPPORTED", "UNSUPPORTED_OPERATION", operation) from exc

    def _op_derive_record_identity(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = record_from_json(payload["record"])
        canonical = record_identity_bytes(record)
        digest = record_identity(record)
        return {
            "identity_bytes_hex": canonical.hex(),
            "identity_bytes_length": len(canonical),
            "record_identity_digest_hex": digest.hex(),
            "record_identity_text": record_identity_text(digest),
        }

    def _op_derive_record_commitment(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = record_from_json(payload["record"])
        commitment = record_commitment(record, payload.get("algorithm", -16))
        return commitment_to_json(commitment)

    def _op_encode_proof_input(self, payload: dict[str, Any]) -> dict[str, Any]:
        commitment = RecordCommitment(
            algorithm=payload["record_commitment"]["algorithm"],
            digest=bytes.fromhex(payload["record_commitment"]["digest_hex"]),
        )
        value = build_proof_input(
            cryptosuite=payload["cryptosuite"],
            proof_purpose=payload["proof_purpose"],
            verification_method=payload["verification_method"],
            record_commitment=commitment,
            created=payload.get("created"),
            expires=payload.get("expires"),
            domain=payload.get("domain"),
            challenge=bytes.fromhex(payload["challenge_hex"]) if payload.get("challenge_hex") else None,
            nonce=bytes.fromhex(payload["nonce_hex"]) if payload.get("nonce_hex") else None,
            extensions=decode_value(payload.get("extensions", {})),
            critical=payload.get("critical", ()),
        )
        encoded = encode_proof_input(value)
        return {"proof_input_hex": encoded.hex(), "proof_input_length": len(encoded)}

    def _op_create_proof(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = record_from_json(payload["record"])
        cfg = payload["proof_configuration"]
        proof = create_proof(
            record,
            proof_purpose=cfg["proof_purpose"],
            verification_method=cfg["verification_method"],
            private_key=bytes.fromhex(payload["private_seed_hex"]),
            cryptosuite=cfg.get("cryptosuite", MANDATORY_CRYPTOSUITE),
            commitment_algorithm=cfg.get("commitment_algorithm", -16),
            created=cfg.get("created"),
            expires=cfg.get("expires"),
            domain=cfg.get("domain"),
            challenge=bytes.fromhex(cfg["challenge_hex"]) if cfg.get("challenge_hex") else None,
            nonce=bytes.fromhex(cfg["nonce_hex"]) if cfg.get("nonce_hex") else None,
            extensions=decode_value(cfg.get("extensions", {})),
            critical=cfg.get("critical", ()),
        )
        return {"proof": proof_to_json(proof), "proof_input_hex": proof_input_bytes(proof).hex()}

    def _op_verify_proof(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = record_from_json(payload["record"])
        proof = proof_from_json(payload["proof"])
        context = payload.get("context", {})
        evaluation_time = datetime.fromisoformat(context["evaluation_time"].replace("Z", "+00:00")) if context.get("evaluation_time") else None
        status = MethodStatus(context["verification_method_status"]) if context.get("verification_method_status") else None
        result = verify_proof(
            record,
            proof,
            resolved_method=resolved_method_from_json(payload.get("resolved_method")),
            expected_purpose=context.get("expected_purpose"),
            expected_domain=context.get("expected_domain"),
            expected_challenge=bytes.fromhex(context["expected_challenge_hex"])
            if context.get("expected_challenge_hex")
            else None,
            evaluation_time=evaluation_time,
            verification_method_status=status,
            policy=policy_from_json(payload.get("policy")),
        )
        return result_to_json(result)
