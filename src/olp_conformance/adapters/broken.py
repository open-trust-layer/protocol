"""Intentionally non-conforming adapter used to test the harness itself."""

from __future__ import annotations

from typing import Any

from .reference import ReferenceAdapter


class BrokenAdapter:
    """A deterministic bad implementation that violates two normative rules."""

    def __init__(self) -> None:
        self._reference = ReferenceAdapter()

    @property
    def name(self) -> str:
        return "intentionally-broken"

    def capabilities(self) -> frozenset[str]:
        return self._reference.capabilities()

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        output = self._reference.execute(operation, payload)
        if operation == "derive_record_identity":
            digest = output["record_identity_digest_hex"]
            output["record_identity_digest_hex"] = ("00" if digest[:2] != "00" else "ff") + digest[2:]
        elif operation == "verify_proof" and output.get("cryptographic_validity") == "INVALID":
            output["cryptographic_validity"] = "VALID"
        return output
