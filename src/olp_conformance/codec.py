"""JSON projection helpers shared by built-in adapters and official vectors."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from olp.model.proof import OLPProof, RecordCommitment
from olp.model.record import RecordV1
from olp.model.verification import (
    MethodStatus,
    ReasonCode,
    ResolvedVerificationMethod,
    ResolutionProvenance,
    VerificationPolicy,
    VerificationResult,
)


def decode_value(value: Any) -> Any:
    """Decode the conformance JSON projection into an abstract OLP value.

    ``$bytes`` represents byte strings. ``$map`` is the escape hatch for
    integer-keyed maps and for literal maps that would otherwise collide with
    a wrapper name. Ordinary JSON objects remain the compact representation
    for unambiguous text-keyed maps.
    """

    if isinstance(value, list):
        return tuple(decode_value(item) for item in value)
    if isinstance(value, dict):
        if set(value) == {"$bytes"}:
            raw = value["$bytes"]
            if not isinstance(raw, str):
                raise ValueError("$bytes MUST contain a hexadecimal string")
            return bytes.fromhex(raw)
        if set(value) == {"$map"}:
            entries = value["$map"]
            if not isinstance(entries, list):
                raise ValueError("$map MUST contain an array of [key, value] pairs")
            result: dict[str | int, Any] = {}
            for entry in entries:
                if not isinstance(entry, list) or len(entry) != 2:
                    raise ValueError("$map entries MUST be two-element arrays")
                key = decode_value(entry[0])
                if isinstance(key, bool) or not isinstance(key, (str, int)):
                    raise ValueError("$map keys MUST be text strings or integer labels")
                if key in result:
                    raise ValueError("$map contains a duplicate abstract key")
                result[key] = decode_value(entry[1])
            return result
        return {key: decode_value(item) for key, item in value.items()}
    return value


def encode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"$bytes": value.hex()}
    if isinstance(value, tuple):
        return [encode_value(item) for item in value]
    if isinstance(value, Mapping):
        keys = tuple(value.keys())
        if all(isinstance(key, str) for key in keys) and set(keys) not in ({"$bytes"}, {"$map"}):
            return {key: encode_value(item) for key, item in value.items()}
        entries = []
        for key, item in value.items():
            if isinstance(key, bool) or not isinstance(key, (str, int)):
                raise TypeError("conformance value-map keys MUST be strings or integers")
            entries.append([encode_value(key), encode_value(item)])
        return {"$map": entries}
    return value


def record_from_json(value: dict[str, Any]) -> RecordV1:
    decoded = decode_value(value)
    return RecordV1.from_mapping(decoded)


def commitment_from_json(value: dict[str, Any]) -> RecordCommitment:
    return RecordCommitment(algorithm=value["algorithm"], digest=bytes.fromhex(value["digest_hex"]))


def commitment_to_json(value: RecordCommitment) -> dict[str, Any]:
    return {"algorithm": value.algorithm, "digest_hex": value.digest.hex()}


def proof_from_json(value: dict[str, Any]) -> OLPProof:
    extensions = decode_value(value.get("extensions", {}))
    return OLPProof(
        type=value.get("type", "OLPProof"),
        version=value["version"],
        cryptosuite=value["cryptosuite"],
        proofPurpose=value["proofPurpose"],
        verificationMethod=value["verificationMethod"],
        recordCommitment=commitment_from_json(value["recordCommitment"]),
        proofValue=bytes.fromhex(value["proofValue_hex"]),
        created=value.get("created"),
        expires=value.get("expires"),
        domain=value.get("domain"),
        challenge=bytes.fromhex(value["challenge_hex"]) if value.get("challenge_hex") is not None else None,
        nonce=bytes.fromhex(value["nonce_hex"]) if value.get("nonce_hex") is not None else None,
        critical=tuple(value.get("critical", ())),
        extensions=extensions,
    )


def proof_to_json(value: OLPProof) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": value.type,
        "version": value.version,
        "cryptosuite": value.cryptosuite,
        "proofPurpose": value.proofPurpose,
        "verificationMethod": value.verificationMethod,
        "recordCommitment": commitment_to_json(value.recordCommitment),
        "proofValue_hex": value.proofValue.hex(),
        "critical": list(value.critical),
        "extensions": encode_value(value.extensions),
    }
    for key in ("created", "expires", "domain"):
        item = getattr(value, key)
        if item is not None:
            result[key] = item
    if value.challenge is not None:
        result["challenge_hex"] = value.challenge.hex()
    if value.nonce is not None:
        result["nonce_hex"] = value.nonce.hex()
    return result


def resolved_method_from_json(value: dict[str, Any] | None) -> ResolvedVerificationMethod | None:
    if value is None:
        return None
    return ResolvedVerificationMethod(
        identifier=value["identifier"],
        key_type=value["key_type"],
        public_key=bytes.fromhex(value["public_key_hex"]),
        provenance=ResolutionProvenance(value.get("provenance", "supplied")),
    )


def policy_from_json(value: dict[str, Any] | None) -> VerificationPolicy:
    defaults = VerificationPolicy()
    if not value:
        return defaults

    if "allowed_commitment_algorithms" in value:
        raw_commitments = value["allowed_commitment_algorithms"]
        allowed_commitments = None if raw_commitments is None else frozenset(raw_commitments)
    else:
        allowed_commitments = defaults.allowed_commitment_algorithms

    if "allowed_cryptosuites" in value:
        raw_suites = value["allowed_cryptosuites"]
        allowed_suites = None if raw_suites is None else frozenset(raw_suites)
    else:
        allowed_suites = defaults.allowed_cryptosuites

    return VerificationPolicy(
        understood_extensions=frozenset(value.get("understood_extensions", defaults.understood_extensions)),
        understood_proof_purposes=frozenset(value.get("understood_proof_purposes", defaults.understood_proof_purposes)),
        allowed_commitment_algorithms=allowed_commitments,
        allowed_cryptosuites=allowed_suites,
    )


def result_to_json(value: VerificationResult) -> dict[str, Any]:
    def enum_value(item: Any) -> Any:
        return item.value if hasattr(item, "value") else item

    return {
        "conformance": enum_value(value.conformance),
        "record_binding": enum_value(value.record_binding),
        "version_support": enum_value(value.version_support),
        "cryptosuite_support": enum_value(value.cryptosuite_support),
        "commitment_algorithm_support": enum_value(value.commitment_algorithm_support),
        "critical_extension_status": enum_value(value.critical_extension_status),
        "verification_method_resolution": enum_value(value.verification_method_resolution),
        "verification_method_compatibility": enum_value(value.verification_method_compatibility),
        "cryptographic_validity": enum_value(value.cryptographic_validity),
        "purpose_status": enum_value(value.purpose_status),
        "domain_status": enum_value(value.domain_status),
        "challenge_status": enum_value(value.challenge_status),
        "temporal_status": enum_value(value.temporal_status),
        "verification_method_status": enum_value(value.verification_method_status),
        "resolution_provenance": enum_value(value.resolution_provenance) if value.resolution_provenance else None,
        "warning_codes": [issue.code.value for issue in value.warnings],
        "error_codes": [issue.code.value for issue in value.errors],
        "warnings": [{"code": issue.code.value, "message": issue.message} for issue in value.warnings],
        "errors": [{"code": issue.code.value, "message": issue.message} for issue in value.errors],
    }
