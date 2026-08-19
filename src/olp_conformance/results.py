"""Machine-readable conformance result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class CaseStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNSUPPORTED = "UNSUPPORTED"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class CaseResult:
    id: str
    capability: str
    category: str
    operation: str
    status: CaseStatus
    expected: dict[str, Any]
    observed: dict[str, Any] | None = None
    message: str | None = None
    vector: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value


@dataclass(frozen=True, slots=True)
class RunReport:
    harness_version: str
    manifest_version: int
    adapter: str
    capabilities: tuple[str, ...]
    results: tuple[CaseResult, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> int:
        return sum(item.status == CaseStatus.PASS for item in self.results)

    @property
    def failed(self) -> int:
        return sum(item.status == CaseStatus.FAIL for item in self.results)

    @property
    def unsupported(self) -> int:
        return sum(item.status == CaseStatus.UNSUPPORTED for item in self.results)

    @property
    def errors(self) -> int:
        return sum(item.status == CaseStatus.ERROR for item in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def overall(self) -> str:
        if self.failed or self.errors:
            return "FAIL"
        if self.unsupported:
            return "PARTIAL"
        return "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "olp-conformance-report-v1",
            "harness_version": self.harness_version,
            "manifest_version": self.manifest_version,
            "adapter": self.adapter,
            "capabilities": list(self.capabilities),
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "unsupported": self.unsupported,
                "errors": self.errors,
                "overall": self.overall,
            },
            "metadata": self.metadata,
            "results": [item.to_dict() for item in self.results],
        }
