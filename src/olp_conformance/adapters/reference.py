"""Adapter for the Python OLP reference implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from olp.constants import MANDATORY_CRYPTOSUITE
from olp.crypto.commitments import record_commitment
from olp.crypto.proof import create_proof, verify_proof
from olp.encoding.proof_input import build_proof_input, encode_proof_input, proof_input_bytes
from olp.encoding.proof_identity import proof_identity, proof_identity_bytes
from olp.encoding.record_identity import record_identity, record_identity_bytes, record_identity_text
from olp.evidence import parse_relationship_record
from olp.bundle import PackagedResourceV1, process_bundle
from olp.model.bundle import ResourceRefV1
from olp.model.evidence import EvidenceRefV1
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
        "olp.proof-identity.v1",
        "olp.evidence-ref.v1",
        "olp.evidence-relationship.v1",
        "olp.bundle.v1",
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


    def _op_derive_proof_identity(self, payload: dict[str, Any]) -> dict[str, Any]:
        proof = proof_from_json(payload["proof"])
        encoded = proof_identity_bytes(proof)
        digest = proof_identity(proof)
        return {
            "proof_identity_bytes_hex": encoded.hex(),
            "proof_identity_bytes_length": len(encoded),
            "proof_identity_digest_hex": digest.hex(),
        }

    def _op_encode_evidence_ref(self, payload: dict[str, Any]) -> dict[str, Any]:
        ref = EvidenceRefV1(payload["kind"], bytes.fromhex(payload["identity_digest_hex"]))
        encoded = ref.canonical_bytes()
        return {
            "evidence_ref_hex": encoded.hex(),
            "evidence_ref_length": len(encoded),
        }

    def _op_process_relationship(self, payload: dict[str, Any]) -> dict[str, Any]:
        record = record_from_json(payload["record"])
        statement = parse_relationship_record(
            record,
            understood_critical_qualifiers=frozenset(payload.get("understood_critical_qualifiers", ())),
            allow_unknown_relation=bool(payload.get("allow_unknown_relation", False)),
        )
        digest = record_identity(record)
        understood = frozenset(payload.get("understood_critical_qualifiers", ()))
        uninterpreted = sorted(set(statement.qualifiers) - set(understood), key=lambda item: item.encode("utf-8"))
        return {
            "relationship_record_identity_hex": digest.hex(),
            "relation_type": statement.relation_type,
            "uninterpreted_qualifiers": uninterpreted,
            "subject": None if statement.subject is None else {
                "kind": int(statement.subject.kind),
                "identity_digest_hex": statement.subject.identity_digest.hex(),
            },
            "objects": [
                {"kind": int(item.kind), "identity_digest_hex": item.identity_digest.hex()} for item in statement.objects
            ],
            "critical": list(statement.critical),
            "projected_edges": [
                {
                    "subject": None if statement.subject is None else {
                        "kind": int(statement.subject.kind),
                        "identity_digest_hex": statement.subject.identity_digest.hex(),
                    },
                    "relation_type": statement.relation_type,
                    "object": {"kind": int(item.kind), "identity_digest_hex": item.identity_digest.hex()},
                    "relationship_record_identity_hex": digest.hex(),
                } for item in statement.objects
            ],
        }

    def _op_process_bundle(self, payload: dict[str, Any]) -> dict[str, Any]:
        manifest = record_from_json(payload["manifest_record"])
        records = [record_from_json(item) for item in payload.get("records", ())]
        proofs = [proof_from_json(item) for item in payload.get("proofs", ())]
        resources = []
        for item in payload.get("resources", ()):
            raw = item["resource_ref"]
            ref = ResourceRefV1(
                raw.get("resource_id"),
                raw["media_type"],
                raw.get("hash_algorithm", -16),
                bytes.fromhex(raw["digest_hex"]),
            )
            resources.append(PackagedResourceV1(ref, bytes.fromhex(item["content_hex"])))
        return process_bundle(
            manifest,
            records=records,
            proofs=proofs,
            resources=resources,
            understood_critical_extensions=frozenset(payload.get("understood_critical_extensions", ())),
        )

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
