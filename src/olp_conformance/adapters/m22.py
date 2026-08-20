"""Milestone 22 extension of the Python reference conformance adapter."""

from __future__ import annotations

from olp.disclosure import plan_disclosure

from ..codec import decode_value, proof_from_json, record_from_json
from .m21 import ReferenceAdapter as M21ReferenceAdapter

M22_CAPABILITY = "olp.privacy-disclosure.v1"


class ReferenceAdapter(M21ReferenceAdapter):
    """Reference adapter extended with the Specification 0010 planner core."""

    def capabilities(self) -> frozenset[str]:
        return super().capabilities() | {M22_CAPABILITY}

    def _op_plan_disclosure(self, payload):
        decoded = decode_value(payload)
        inventory = []
        raw_inventory = payload.get("inventory", ())
        for index, decoded_item in enumerate(decoded.get("inventory", ())):
            item = dict(decoded_item)
            raw_item = raw_inventory[index]
            if "record" in raw_item:
                item["record"] = record_from_json(raw_item["record"])
            if "proof" in raw_item:
                item["proof"] = proof_from_json(raw_item["proof"])
            inventory.append(item)

        resources = []
        raw_resources = payload.get("resources", ())
        for index, decoded_item in enumerate(decoded.get("resources", ())):
            item = dict(decoded_item)
            raw_item = raw_resources[index]
            if "content_hex" in raw_item:
                item.pop("content_hex", None)
                item["content"] = bytes.fromhex(raw_item["content_hex"])
            resources.append(item)

        prepared = dict(decoded)
        prepared["inventory"] = tuple(inventory)
        prepared["resources"] = tuple(resources)
        return plan_disclosure(prepared)
