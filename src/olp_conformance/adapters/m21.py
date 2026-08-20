"""Milestone 21 extension of the Python reference conformance adapter."""

from __future__ import annotations

from olp.identity_authority_lifecycle_v1 import evaluate_authority_lifecycle

from ..codec import decode_value
from .reference import ReferenceAdapter as CoreReferenceAdapter

M21_CAPABILITY = "olp.identity-authority-lifecycle.v1"


class ReferenceAdapter(CoreReferenceAdapter):
    """Reference adapter extended with the Specifications 0006/0007 core slice."""

    def capabilities(self) -> frozenset[str]:
        return super().capabilities() | {M21_CAPABILITY}

    def _op_evaluate_authority_lifecycle(self, payload):
        # Official JSON vectors use the harness lossless projection. Decode it
        # before semantic evaluation so $bytes remains raw OLP byte strings.
        return evaluate_authority_lifecycle(decode_value(payload))
