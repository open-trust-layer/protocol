"""Specification 0008 bundle manifest and resource reference models."""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from ..encoding.deterministic_cbor import encode
from ..errors import ConformanceError, UnsupportedFeatureError
from ..model.evidence import EvidenceRefV1
from ..values import freeze_value, is_absolute_uri, validate_record_value

BUNDLE_DOMAIN = "OLP-EVIDENCE-BUNDLE-MANIFEST"
BUNDLE_VERSION = 1
CORE_BUNDLE_PROFILES = frozenset({"portable", "selfContainedVerification"})
_MEDIA_TYPE_RE = re.compile(r"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$")

@dataclass(frozen=True, slots=True, order=True)
class ResourceRefV1:
    resource_id: str | None
    media_type: str
    hash_algorithm: int
    digest: bytes

    def __post_init__(self) -> None:
        digest = bytes(self.digest) if isinstance(self.digest, bytearray) else self.digest
        object.__setattr__(self, "digest", digest)

    @classmethod
    def from_value(cls, value: Any) -> "ResourceRefV1":
        if not isinstance(value, (tuple, list)) or len(value) != 4:
            raise ConformanceError("ResourceRefV1 MUST be a four-element array", code="MALFORMED_RESOURCE_REF")
        ref = cls(value[0], value[1], value[2], value[3])
        ref.validate()
        return ref

    def validate(self) -> None:
        if self.resource_id is not None and not is_absolute_uri(self.resource_id):
            raise ConformanceError("resourceId MUST be an absolute URI or null", code="MALFORMED_RESOURCE_REF")
        if not isinstance(self.media_type, str) or not _MEDIA_TYPE_RE.fullmatch(self.media_type):
            raise ConformanceError("mediaType MUST be lowercase type/subtype without parameters", code="MALFORMED_RESOURCE_REF")
        if isinstance(self.hash_algorithm, bool) or not isinstance(self.hash_algorithm, int):
            raise ConformanceError("hashAlgorithmId MUST be an integer", code="MALFORMED_RESOURCE_REF")
        if self.hash_algorithm != -16:
            raise UnsupportedFeatureError("unsupported resource hash algorithm", code="UNSUPPORTED_RESOURCE_HASH_ALGORITHM")
        if not isinstance(self.digest, bytes) or len(self.digest) != 32:
            raise ConformanceError("SHA-256 ResourceRefV1 digest MUST contain 32 octets", code="MALFORMED_RESOURCE_REF")

    def to_value(self) -> tuple[Any, ...]:
        return (self.resource_id, self.media_type, self.hash_algorithm, self.digest)

    def canonical_bytes(self) -> bytes:
        self.validate()
        return encode(self.to_value())

@dataclass(frozen=True, slots=True)
class BundleManifestStatementV1:
    profile: str
    roots: tuple[EvidenceRefV1, ...]
    inventory: tuple[EvidenceRefV1, ...]
    resource_inventory: tuple[ResourceRefV1, ...] = ()
    metadata: Mapping[int, Any] = field(default_factory=dict)
    extensions: Mapping[str, Any] = field(default_factory=dict)
    critical: tuple[str, ...] = ()
    version: int = BUNDLE_VERSION
    domain: str = BUNDLE_DOMAIN

    def __post_init__(self) -> None:
        object.__setattr__(self, "roots", tuple(self.roots))
        object.__setattr__(self, "inventory", tuple(self.inventory))
        object.__setattr__(self, "resource_inventory", tuple(self.resource_inventory))
        object.__setattr__(self, "metadata", MappingProxyType({k: freeze_value(v) for k, v in self.metadata.items()}))
        object.__setattr__(self, "extensions", MappingProxyType({k: freeze_value(v) for k, v in self.extensions.items()}))
        object.__setattr__(self, "critical", tuple(self.critical))

    @classmethod
    def from_value(cls, value: Any) -> "BundleManifestStatementV1":
        if not isinstance(value, (tuple, list)) or len(value) != 9:
            raise ConformanceError("BundleManifestStatementV1 MUST contain nine elements", code="MALFORMED_BUNDLE_MANIFEST")
        domain, version, profile, roots, inventory, resources, metadata, extensions, critical = value
        if not isinstance(roots, (tuple, list)) or not isinstance(inventory, (tuple, list)) or not isinstance(resources, (tuple, list)):
            raise ConformanceError("bundle roots/inventory/resources MUST be arrays", code="MALFORMED_BUNDLE_MANIFEST")
        if not isinstance(metadata, Mapping) or not isinstance(extensions, Mapping) or not isinstance(critical, (tuple, list)):
            raise ConformanceError("bundle metadata/extensions/critical have invalid types", code="MALFORMED_BUNDLE_MANIFEST")
        return cls(
            domain=domain,
            version=version,
            profile=profile,
            roots=tuple(EvidenceRefV1.from_value(v) for v in roots),
            inventory=tuple(EvidenceRefV1.from_value(v) for v in inventory),
            resource_inventory=tuple(ResourceRefV1.from_value(v) for v in resources),
            metadata=metadata,
            extensions=extensions,
            critical=tuple(critical),
        )

    def to_value(self) -> tuple[Any, ...]:
        return (
            self.domain,
            self.version,
            self.profile,
            tuple(v.to_value() for v in self.roots),
            tuple(v.to_value() for v in self.inventory),
            tuple(v.to_value() for v in self.resource_inventory),
            self.metadata,
            self.extensions,
            self.critical,
        )

    def validate(self, *, understood_critical_extensions: frozenset[str] = frozenset()) -> None:
        if self.domain != BUNDLE_DOMAIN:
            raise ConformanceError("invalid bundle manifest discriminator", code="MALFORMED_BUNDLE_MANIFEST")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ConformanceError("bundle manifest version MUST be integer", code="MALFORMED_BUNDLE_MANIFEST")
        if self.version != BUNDLE_VERSION:
            raise UnsupportedFeatureError("unsupported bundle manifest version", code="UNSUPPORTED_BUNDLE_MANIFEST_VERSION")
        if not isinstance(self.profile, str) or not self.profile:
            raise ConformanceError("bundle profile MUST be text", code="MALFORMED_BUNDLE_MANIFEST")
        if self.profile not in CORE_BUNDLE_PROFILES:
            if not is_absolute_uri(self.profile):
                raise ConformanceError("extension bundle profile MUST be an absolute URI", code="MALFORMED_BUNDLE_MANIFEST")
            raise UnsupportedFeatureError("unsupported bundle profile", code="UNSUPPORTED_BUNDLE_PROFILE")

        self._validate_sorted_unique_refs(self.roots, "roots")
        self._validate_sorted_unique_refs(self.inventory, "inventory")
        inv_set = set(self.inventory)
        if any(root not in inv_set for root in self.roots):
            raise ConformanceError("every core-profile root MUST be present in inventory", code="BUNDLE_ROOT_NOT_IN_INVENTORY")

        resource_bytes = [ref.canonical_bytes() for ref in self.resource_inventory]
        if len(resource_bytes) != len(set(resource_bytes)):
            raise ConformanceError("duplicate resource inventory entry", code="DUPLICATE_BUNDLE_RESOURCE")
        if resource_bytes != sorted(resource_bytes):
            raise ConformanceError("resource inventory is not canonically sorted", code="NON_CANONICAL_BUNDLE_RESOURCE_ORDER")

        allowed_meta = {0, 1, 2}
        for key, value in self.metadata.items():
            if isinstance(key, bool) or not isinstance(key, int) or key not in allowed_meta:
                raise ConformanceError("unknown BundleManifestStatementV1 metadata label", code="MALFORMED_BUNDLE_METADATA")
            validate_record_value(value, path=f"bundle.metadata[{key}]")
        if self.metadata.get(0) is not None and not is_absolute_uri(self.metadata.get(0)):
            raise ConformanceError("declaredPurpose MUST be absolute URI or null", code="MALFORMED_BUNDLE_METADATA")
        for key, value in self.extensions.items():
            if not is_absolute_uri(key):
                raise ConformanceError("bundle extension key MUST be absolute URI", code="MALFORMED_BUNDLE_EXTENSION")
            validate_record_value(value, path=f"bundle.extensions[{key!r}]")
        if len(self.critical) != len(set(self.critical)):
            raise ConformanceError("duplicate bundle critical extension", code="MALFORMED_BUNDLE_EXTENSION")
        if self.critical != tuple(sorted(self.critical, key=lambda x: x.encode("utf-8"))):
            raise ConformanceError("bundle critical extensions must be sorted", code="MALFORMED_BUNDLE_EXTENSION")
        for key in self.critical:
            if not is_absolute_uri(key) or key not in self.extensions:
                raise ConformanceError("critical bundle extension must name a present extension", code="MALFORMED_BUNDLE_EXTENSION")
        if set(self.critical) - set(understood_critical_extensions):
            raise UnsupportedFeatureError("unsupported critical bundle extension", code="UNSUPPORTED_CRITICAL_BUNDLE_EXTENSION")

    @staticmethod
    def _validate_sorted_unique_refs(values: tuple[EvidenceRefV1, ...], label: str) -> None:
        canonical = [v.canonical_bytes() for v in values]
        if len(canonical) != len(set(canonical)):
            raise ConformanceError(f"duplicate bundle {label} entry", code=f"DUPLICATE_BUNDLE_{label.upper()}")
        if canonical != sorted(canonical):
            raise ConformanceError(f"bundle {label} is not canonically sorted", code=f"NON_CANONICAL_BUNDLE_{label.upper()}_ORDER")
