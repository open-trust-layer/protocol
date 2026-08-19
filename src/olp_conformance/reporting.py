"""Human and JSON report rendering."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .results import CaseStatus, RunReport


def render_console(report: RunReport) -> str:
    grouped: dict[tuple[str, str], list] = defaultdict(list)
    for result in report.results:
        grouped[(result.capability, result.category)].append(result)

    lines = ["Open Layer Protocol Conformance", f"Adapter: {report.adapter}", ""]
    for (capability, category), items in sorted(grouped.items()):
        passed = sum(item.status == CaseStatus.PASS for item in items)
        failed = sum(item.status == CaseStatus.FAIL for item in items)
        unsupported = sum(item.status == CaseStatus.UNSUPPORTED for item in items)
        errors = sum(item.status == CaseStatus.ERROR for item in items)
        suffix = f"{passed}/{len(items)} PASS"
        extras = []
        if failed:
            extras.append(f"{failed} FAIL")
        if unsupported:
            extras.append(f"{unsupported} UNSUPPORTED")
        if errors:
            extras.append(f"{errors} ERROR")
        if extras:
            suffix += " | " + " | ".join(extras)
        lines.append(f"{capability} [{category}]".ljust(66) + suffix)

    lines.extend(
        [
            "",
            "-" * 88,
            f"Total: {report.total} | PASS: {report.passed} | FAIL: {report.failed} | "
            f"UNSUPPORTED: {report.unsupported} | ERROR: {report.errors}",
            f"Result: {report.overall}",
        ]
    )
    failures = [item for item in report.results if item.status in {CaseStatus.FAIL, CaseStatus.ERROR}]
    if failures:
        lines.append("")
        lines.append("Failures:")
        for item in failures:
            lines.append(f"  {item.id}: {item.message or item.status.value}")
    return "\n".join(lines)


def write_json_report(report: RunReport, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
