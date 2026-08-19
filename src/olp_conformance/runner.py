"""Conformance case execution and expectation matching."""

from __future__ import annotations

from typing import Any, Iterable

from .adapter import AdapterExecutionError, ConformanceAdapter
from .manifest import ConformanceCase, ConformanceManifest, load_vector
from .results import CaseResult, CaseStatus, RunReport


def _subset_matches(expected: Any, observed: Any, path: str = "$") -> tuple[bool, str | None]:
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            return False, f"{path}: expected object, observed {type(observed).__name__}"
        for key, value in expected.items():
            if key not in observed:
                return False, f"{path}: missing key {key!r}"
            ok, message = _subset_matches(value, observed[key], f"{path}.{key}")
            if not ok:
                return ok, message
        return True, None
    if isinstance(expected, list):
        if not isinstance(observed, list):
            return False, f"{path}: expected list, observed {type(observed).__name__}"
        if len(expected) != len(observed):
            return False, f"{path}: expected list length {len(expected)}, observed {len(observed)}"
        for index, value in enumerate(expected):
            ok, message = _subset_matches(value, observed[index], f"{path}[{index}]")
            if not ok:
                return ok, message
        return True, None
    if expected != observed:
        return False, f"{path}: expected {expected!r}, observed {observed!r}"
    return True, None


class ConformanceRunner:
    def __init__(self, manifest: ConformanceManifest, adapter: ConformanceAdapter) -> None:
        self.manifest = manifest
        self.adapter = adapter

    def run(
        self,
        *,
        categories: Iterable[str] | None = None,
        capabilities: Iterable[str] | None = None,
        case_ids: Iterable[str] | None = None,
        profile: str | None = None,
    ) -> RunReport:
        category_filter = set(categories or ())
        capability_filter = set(capabilities or ())
        id_filter = set(case_ids or ())
        if profile:
            try:
                profile_caps = set(self.manifest.profiles[profile])
            except KeyError as exc:
                raise ValueError(f"unknown conformance profile {profile!r}") from exc
            capability_filter = capability_filter & profile_caps if capability_filter else profile_caps

        adapter_caps = self.adapter.capabilities()
        results: list[CaseResult] = []
        for case in self.manifest.cases:
            if category_filter and case.category not in category_filter:
                continue
            if capability_filter and case.capability not in capability_filter:
                continue
            if id_filter and case.id not in id_filter:
                continue
            results.append(self._run_case(case, adapter_caps))

        return RunReport(
            harness_version=self.manifest.harness_version,
            manifest_version=self.manifest.version,
            adapter=self.adapter.name,
            capabilities=tuple(sorted(adapter_caps)),
            results=tuple(results),
        )

    def _run_case(self, case: ConformanceCase, adapter_caps: frozenset[str]) -> CaseResult:
        vector = load_vector(self.manifest, case)
        expected = vector["expected"]
        if case.capability not in adapter_caps:
            return CaseResult(
                id=case.id,
                capability=case.capability,
                category=case.category,
                operation=case.operation,
                status=CaseStatus.UNSUPPORTED,
                expected=expected,
                message="adapter does not declare required capability",
                vector=case.vector,
            )

        try:
            observed_output = self.adapter.execute(case.operation, vector["input"])
        except AdapterExecutionError as exc:
            observed = {
                "outcome": "ERROR",
                "classification": exc.classification,
                "reason": exc.reason,
            }
            if expected.get("outcome") != "ERROR":
                return self._failed(case, expected, observed, str(exc))
            ok, message = _subset_matches(expected, observed)
            return CaseResult(
                id=case.id,
                capability=case.capability,
                category=case.category,
                operation=case.operation,
                status=CaseStatus.PASS if ok else CaseStatus.FAIL,
                expected=expected,
                observed=observed,
                message=message,
                vector=case.vector,
            )
        except Exception as exc:  # harness-level adapter crash, not a protocol classification
            return CaseResult(
                id=case.id,
                capability=case.capability,
                category=case.category,
                operation=case.operation,
                status=CaseStatus.ERROR,
                expected=expected,
                observed={"exception": type(exc).__name__},
                message=str(exc),
                vector=case.vector,
            )

        observed = {"outcome": "SUCCESS", "result": observed_output}
        if expected.get("outcome") != "SUCCESS":
            return self._failed(case, expected, observed, "operation succeeded but an error was expected")
        ok, message = _subset_matches(expected, observed)
        return CaseResult(
            id=case.id,
            capability=case.capability,
            category=case.category,
            operation=case.operation,
            status=CaseStatus.PASS if ok else CaseStatus.FAIL,
            expected=expected,
            observed=observed,
            message=message,
            vector=case.vector,
        )

    @staticmethod
    def _failed(case: ConformanceCase, expected: dict[str, Any], observed: dict[str, Any], message: str) -> CaseResult:
        return CaseResult(
            id=case.id,
            capability=case.capability,
            category=case.category,
            operation=case.operation,
            status=CaseStatus.FAIL,
            expected=expected,
            observed=observed,
            message=message,
            vector=case.vector,
        )
