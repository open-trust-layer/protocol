"""Milestone 23 transport-encoding extension of the Python reference adapter."""

from __future__ import annotations

from olp.encoding.proof_identity import proof_identity
from olp.encoding.record_identity import record_identity
from olp.model.proof import OLPProof, RecordCommitment
from olp.model.record import RecordV1
from olp.transport import (
    OJVEMap,
    TransportEnvelopeV1,
    decode_identity_text,
    decode_ojve,
    encode_identity_text,
    encode_ojve,
    materialize_map,
    project_abstract,
    unproject_abstract,
)

from ..codec import proof_from_json
from .m22 import ReferenceAdapter as M22ReferenceAdapter

M23_CAPABILITY = "olp.transport-encoding.v1"


def _proof_to_abstract(proof: OLPProof) -> OJVEMap:
    entries: list[tuple[object, object]] = [
        ("type", proof.type),
        ("version", proof.version),
        ("cryptosuite", proof.cryptosuite),
        ("proofPurpose", proof.proofPurpose),
        ("verificationMethod", proof.verificationMethod),
        ("recordCommitment", (proof.recordCommitment.algorithm, proof.recordCommitment.digest)),
        ("proofValue", proof.proofValue),
    ]
    for key in ("created", "expires", "domain"):
        value = getattr(proof, key)
        if value is not None:
            entries.append((key, value))
    if proof.challenge is not None:
        entries.append(("challenge", proof.challenge))
    if proof.nonce is not None:
        entries.append(("nonce", proof.nonce))
    entries.append(("critical", proof.critical))
    entries.append(("extensions", OJVEMap(proof.extensions.items())))
    return OJVEMap(entries)


def _proof_from_abstract(value: object) -> OLPProof:
    mapping = materialize_map(value, allowed_key_types=(str, int))
    if not isinstance(mapping, dict):
        raise ValueError("transported proof payload must be a map")
    commitment = mapping["recordCommitment"]
    if not isinstance(commitment, tuple) or len(commitment) != 2:
        raise ValueError("transported recordCommitment must be a two-element array")
    proof = OLPProof(
        type=mapping["type"],
        version=mapping["version"],
        cryptosuite=mapping["cryptosuite"],
        proofPurpose=mapping["proofPurpose"],
        verificationMethod=mapping["verificationMethod"],
        recordCommitment=RecordCommitment(commitment[0], commitment[1]),
        proofValue=mapping["proofValue"],
        created=mapping.get("created"),
        expires=mapping.get("expires"),
        domain=mapping.get("domain"),
        challenge=mapping.get("challenge"),
        nonce=mapping.get("nonce"),
        critical=tuple(mapping.get("critical", ())),
        extensions=mapping.get("extensions", {}),
    )
    proof.validate_structure()
    return proof


class ReferenceAdapter(M22ReferenceAdapter):
    """Reference adapter extended with Specification 0012 M23 encoding."""

    def capabilities(self) -> frozenset[str]:
        return super().capabilities() | {M23_CAPABILITY}

    def _op_encode_identity_text(self, payload):
        text = encode_identity_text(payload["kind"], bytes.fromhex(payload["digest_hex"]))
        return {"text": text}

    def _op_decode_identity_text(self, payload):
        kind, digest = decode_identity_text(payload["text"], expected_kind=payload.get("expected_kind"))
        return {"kind": kind, "digest_hex": digest.hex()}

    def _op_encode_ojve(self, payload):
        abstract = unproject_abstract(payload["value"])
        return {"ojve": encode_ojve(abstract)}

    def _op_decode_ojve(self, payload):
        abstract = decode_ojve(payload["ojve"])
        return {"value": project_abstract(abstract)}

    def _op_encode_transport_envelope(self, payload):
        abstract_payload = unproject_abstract(payload["payload"])
        envelope = TransportEnvelopeV1(payload["message_type"], abstract_payload)
        return {
            "json": envelope.to_json(),
            "cbor_hex": envelope.to_cbor().hex(),
            "abstract": project_abstract(envelope.to_abstract()),
        }

    def _op_decode_transport_envelope(self, payload):
        envelope = TransportEnvelopeV1.from_json(payload["json"])
        return {
            "message_type": envelope.message_type,
            "payload": project_abstract(envelope.payload),
            "abstract": project_abstract(envelope.to_abstract()),
        }

    def _op_transport_record_equivalence(self, payload):
        abstract_record = unproject_abstract(payload["record"])
        record_mapping = materialize_map(abstract_record, allowed_key_types=(str,))
        record = RecordV1.from_mapping(record_mapping)
        before = record_identity(record)

        envelope = TransportEnvelopeV1("record", abstract_record)
        json_wire = envelope.to_json()
        decoded = TransportEnvelopeV1.from_json(json_wire)
        decoded_mapping = materialize_map(decoded.payload, allowed_key_types=(str,))
        reconstructed = RecordV1.from_mapping(decoded_mapping)
        after = record_identity(reconstructed)

        return {
            "record_identity_before_hex": before.hex(),
            "record_identity_after_json_hex": after.hex(),
            "identity_preserved": before == after,
            "json": json_wire,
            "cbor_hex": envelope.to_cbor().hex(),
        }

    def _op_transport_proof_equivalence(self, payload):
        proof = proof_from_json(payload["proof"])
        proof.validate_structure()
        before = proof_identity(proof)
        abstract_proof = _proof_to_abstract(proof)

        envelope = TransportEnvelopeV1("proof", abstract_proof)
        json_wire = envelope.to_json()
        decoded = TransportEnvelopeV1.from_json(json_wire)
        reconstructed = _proof_from_abstract(decoded.payload)
        after = proof_identity(reconstructed)

        return {
            "proof_identity_before_hex": before.hex(),
            "proof_identity_after_json_hex": after.hex(),
            "identity_preserved": before == after,
            "proof_value_preserved": reconstructed.proofValue == proof.proofValue,
            "json": json_wire,
            "cbor_hex": envelope.to_cbor().hex(),
        }
