"""Command-line entry point for ``olp-conformance``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .adapter import SubprocessAdapter
from .adapters import BrokenAdapter, ReferenceAdapter
from .commitment import build_profile_corpus_commitment
from .manifest import load_manifest
from .reporting import render_console, write_json_report
from .runner import ConformanceRunner


def _default_manifest() -> Path:
    cwd = Path.cwd() / "conformance" / "manifest.json"
    if cwd.exists():
        return cwd
    # Installed package development fallback: walk upward from this file.
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "conformance" / "manifest.json"
        if candidate.exists():
            return candidate
    return cwd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="olp-conformance", description="Open Layer Protocol executable conformance harness")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run conformance cases")
    run.add_argument("--manifest", type=Path, default=_default_manifest())
    run.add_argument("--adapter", choices=("reference", "broken", "subprocess"), default="reference")
    run.add_argument("--adapter-command", help="command for --adapter subprocess")
    run.add_argument("--profile", default="core-v1")
    run.add_argument("--category", action="append", choices=("positive", "negative", "malformed", "unsupported"))
    run.add_argument("--capability", action="append")
    run.add_argument("--case", action="append", dest="case_ids")
    run.add_argument("--report", type=Path, default=Path("conformance-report.json"))
    run.add_argument("--quiet", action="store_true")

    listing = sub.add_parser("list", help="list manifest cases and profiles")
    listing.add_argument("--manifest", type=Path, default=_default_manifest())
    listing.add_argument("--json", action="store_true")

    commitment = sub.add_parser("commitment", help="compute a deterministic profile corpus commitment")
    commitment.add_argument("--manifest", type=Path, default=_default_manifest())
    commitment.add_argument("--profile", required=True)
    commitment.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "commitment":
        commitment = build_profile_corpus_commitment(args.manifest, args.profile)
        payload = commitment.as_dict()
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"profile: {commitment.profile}")
            print(f"harness: {commitment.harness_version}")
            print(f"capabilities: {len(commitment.capabilities)}")
            print(f"cases: {len(commitment.case_ids)}")
            print(f"files: {len(commitment.files)}")
            print(f"sha-256: {commitment.digest_hex}")
        return 0

    manifest = load_manifest(args.manifest)
    if args.command == "list":
        payload = {
            "profiles": {key: list(value) for key, value in manifest.profiles.items()},
            "cases": [
                {"id": case.id, "capability": case.capability, "category": case.category, "operation": case.operation}
                for case in manifest.cases
            ],
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for profile, caps in manifest.profiles.items():
                print(f"profile {profile}: {', '.join(caps)}")
            print()
            for case in manifest.cases:
                print(f"{case.id:48} {case.category:11} {case.capability}")
        return 0

    if args.adapter == "reference":
        adapter = ReferenceAdapter()
    elif args.adapter == "broken":
        adapter = BrokenAdapter()
    else:
        if not args.adapter_command:
            raise SystemExit("--adapter-command is required for subprocess adapters")
        adapter = SubprocessAdapter(args.adapter_command)

    report = ConformanceRunner(manifest, adapter).run(
        categories=args.category,
        capabilities=args.capability,
        case_ids=args.case_ids,
        profile=args.profile,
    )
    write_json_report(report, args.report)
    if not args.quiet:
        print(render_console(report))
        print(f"\nMachine-readable report: {args.report}")
    return 0 if report.overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
