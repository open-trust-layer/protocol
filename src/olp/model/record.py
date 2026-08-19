"""Specification 0003 record envelope model and validation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from ..errors import ConformanceError
from ..values import freeze_value, is_absolute_uri, is_semantic_identifier, validate_record_value

_RECORD_FIELDS = frozenset(
    {"envelope_version", "type", "content", "semantic_bindings", "profiles", "relationships", "extensions"}
)


@dataclass(frozen=True, slots=True)
class RecordV1:
    envelope_version: int
    type: str
    content: Any
    semantic_bindings: Mapping[str, Any] = field(default_factory=dict)
    profiles: tuple[str, ...] = ()
    relationships: tuple[Any, ...] = ()
    extensions: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "content", freeze_value(self.content))
        object.__setattr__(self, "semantic_bindings", _freeze_mapping(self.semantic_bindings))
        object.__setattr__(self, "profiles", tuple(self.profiles))
        object.__setattr__(self, "relationships", tuple(freeze_value(v) for v in self.relationships))
        object.__setattr__(self, "extensions", _freeze_mapping(self.extensions))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RecordV1":
        unknown = set(value) - _RECORD_FIELDS
        if unknown:
            raise ConformanceError(f"unknown RecordV1 top-level fields: {sorted(unknown)!r}")
        missing = {"envelope_version", "type", "content"} - set(value)
        if missing:
            raise ConformanceError(f"missing required RecordV1 fields: {sorted(missing)!r}")
        return cls(
            envelope_version=value["envelope_version"],
            type=value["type"],
            content=value["content"],
            semantic_bindings=value.get("semantic_bindings", {}),
            profiles=tuple(value.get("profiles", ())),
            relationships=tuple(value.get("relationships", ())),
            extensions=value.get("extensions", {}),
        )

    def validate(self) -> None:
        if self.envelope_version != 1:
            raise ConformanceError("RecordV1 envelope_version MUST equal 1")
        if not is_semantic_identifier(self.type):
            raise ConformanceError("RecordV1 type is not a valid SemanticIdentifier")
        validate_record_value(self.content, path="content")

        if not isinstance(self.semantic_bindings, Mapping):
            raise ConformanceError("semantic_bindings must be a map")
        for key, value in self.semantic_bindings.items():
            if not is_semantic_identifier(key):
                raise ConformanceError(f"semantic_bindings key is not a SemanticIdentifier: {key!r}")
            validate_record_value(value, path=f"semantic_bindings[{key!r}]")

        if len(self.profiles) != len(set(self.profiles)):
            raise ConformanceError("profiles MUST contain unique SemanticIdentifiers")
        for profile in self.profiles:
            if not is_semantic_identifier(profile):
                raise ConformanceError(f"invalid profile SemanticIdentifier: {profile!r}")

        for index, relationship in enumerate(self.relationships):
            validate_record_value(relationship, path=f"relationships[{index}]")

        if not isinstance(self.extensions, Mapping):
            raise ConformanceError("extensions must be a map")
        for key, value in self.extensions.items():
            if not is_absolute_uri(key):
                raise ConformanceError(f"record extension key MUST be an absolute URI: {key!r}")
            validate_record_value(value, path=f"extensions[{key!r}]")

    def identity_preimage(self) -> tuple[Any, ...]:
        self.validate()
        sorted_profiles = tuple(sorted(self.profiles, key=lambda item: item.encode("utf-8")))
        return (
            "OLP-RECORD",
            1,
            self.type,
            self.content,
            self.semantic_bindings,
            sorted_profiles,
            self.relationships,
            self.extensions,
        )


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        return value  # type: ignore[return-value]
    return MappingProxyType({key: freeze_value(item) for key, item in value.items()})
