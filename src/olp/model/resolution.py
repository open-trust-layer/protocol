"""Specification 0009 resolution request model for the executable offline-first core."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from ..errors import ConformanceError, UnsupportedFeatureError
from ..model.evidence import EvidenceRefV1
from ..model.bundle import ResourceRefV1
from ..model.proof import is_rfc3339
from ..values import freeze_value, is_absolute_uri

RESOLUTION_REQUEST_DOMAIN = "OLP-RESOLUTION-REQUEST"
RESOLUTION_REQUEST_VERSION = 1
CORE_TARGET_CLASSES = frozenset({"evidence", "verificationMethod", "principal", "externalResource", "lifecycle", "service"})
SUPPORTED_EXECUTABLE_TARGET_CLASSES = frozenset({"evidence", "externalResource"})
_OPTION_KEYS = frozenset({0, 1, 2, 3, 4, 5})


@dataclass(frozen=True, slots=True)
class ResolutionRequestV1:
    target_class: str
    target: Any
    accept: tuple[str, ...] = ()
    as_of: str | None = None
    options: Mapping[int, Any] = field(default_factory=dict)
    version: int = RESOLUTION_REQUEST_VERSION
    domain: str = RESOLUTION_REQUEST_DOMAIN

    def __post_init__(self) -> None:
        object.__setattr__(self, "accept", tuple(self.accept))
        object.__setattr__(self, "target", freeze_value(self.target))
        object.__setattr__(self, "options", MappingProxyType({k: freeze_value(v) for k, v in self.options.items()}))

    @classmethod
    def from_value(cls, value: Any) -> "ResolutionRequestV1":
        if not isinstance(value, (tuple, list)) or len(value) != 7:
            raise ConformanceError("ResolutionRequestV1 MUST contain seven elements", code="MALFORMED_RESOLUTION_REQUEST")
        domain, version, target_class, target, accept, as_of, options = value
        if not isinstance(accept, (tuple, list)):
            raise ConformanceError("accept MUST be an array", code="MALFORMED_RESOLUTION_REQUEST")
        if not isinstance(options, Mapping):
            raise ConformanceError("options MUST be a map", code="MALFORMED_RESOLUTION_REQUEST")
        request = cls(target_class, target, tuple(accept), as_of, options, version, domain)
        request.validate()
        return request

    def validate(self) -> None:
        if self.domain != RESOLUTION_REQUEST_DOMAIN:
            raise ConformanceError("invalid resolution request discriminator", code="MALFORMED_RESOLUTION_REQUEST")
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ConformanceError("resolution version MUST be integer", code="MALFORMED_RESOLUTION_REQUEST")
        if self.version != RESOLUTION_REQUEST_VERSION:
            raise UnsupportedFeatureError("unsupported resolution request version", code="UNSUPPORTED_RESOLUTION_REQUEST_VERSION")
        if not isinstance(self.target_class, str) or not self.target_class:
            raise ConformanceError("targetClass MUST be text", code="MALFORMED_RESOLUTION_REQUEST")
        if self.target_class not in CORE_TARGET_CLASSES:
            if is_absolute_uri(self.target_class):
                raise UnsupportedFeatureError("unsupported target class", code="UNSUPPORTED_TARGET_CLASS")
            raise ConformanceError("unknown compact target class", code="MALFORMED_RESOLUTION_REQUEST")
        if self.target_class not in SUPPORTED_EXECUTABLE_TARGET_CLASSES:
            raise UnsupportedFeatureError("target class is outside executable resolution-v1", code="UNSUPPORTED_TARGET_CLASS")

        if self.target_class == "evidence":
            EvidenceRefV1.from_value(self.target)
        elif self.target_class == "externalResource":
            if isinstance(self.target, str):
                if not is_absolute_uri(self.target):
                    raise ConformanceError("external resource target MUST be absolute URI", code="MALFORMED_RESOLUTION_REQUEST")
            else:
                ResourceRefV1.from_value(self.target)

        accept = self.accept
        if any(not isinstance(item, str) or not item for item in accept):
            raise ConformanceError("accept members MUST be non-empty text", code="MALFORMED_RESOLUTION_REQUEST")
        if len(set(accept)) != len(accept):
            raise ConformanceError("accept MUST be a set", code="MALFORMED_RESOLUTION_REQUEST")
        if self.as_of is not None and (not isinstance(self.as_of, str) or not is_rfc3339(self.as_of)):
            raise ConformanceError("asOf MUST be RFC 3339 or null", code="MALFORMED_RESOLUTION_REQUEST")

        for key in self.options:
            if isinstance(key, bool) or not isinstance(key, int) or key not in _OPTION_KEYS:
                raise ConformanceError("unknown resolution option", code="MALFORMED_RESOLUTION_REQUEST")
        for key in (0, 3, 4):
            if key in self.options and not isinstance(self.options[key], bool):
                raise ConformanceError("boolean resolution option has invalid type", code="MALFORMED_RESOLUTION_REQUEST")
        for key in (1, 2):
            if key in self.options and self.options[key] is not None:
                value = self.options[key]
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ConformanceError("resolution limit MUST be non-negative integer or null", code="MALFORMED_RESOLUTION_REQUEST")
        if 5 in self.options and self.options[5] is not None and not is_absolute_uri(self.options[5]):
            raise ConformanceError("networkPolicyId MUST be absolute URI or null", code="MALFORMED_RESOLUTION_REQUEST")

    @property
    def offline_only(self) -> bool:
        return bool(self.options.get(0, False))

    @property
    def max_bytes(self) -> int | None:
        return self.options.get(1)

    @property
    def max_results(self) -> int | None:
        return self.options.get(2)

    @property
    def allow_redirects(self) -> bool:
        return bool(self.options.get(3, False))

    @property
    def require_fresh(self) -> bool:
        return bool(self.options.get(4, False))
