"""Reference executable for the language-neutral JSON-lines adapter contract.

This is primarily an interoperability example and self-test target. Independent
implementations can provide an executable in any language as long as it accepts
and returns the same protocol messages.
"""

from __future__ import annotations

import json
import sys

from .adapter import AdapterExecutionError
from .adapters.reference import ReferenceAdapter


def main() -> int:
    lines = [line for line in sys.stdin.read().splitlines() if line.strip()]
    if len(lines) != 1:
        print(json.dumps({"protocol": "olp-conformance-adapter-v1", "ok": False, "error": {"classification": "MALFORMED", "reason": "REQUEST_COUNT", "message": "expected exactly one request"}}))
        return 0
    try:
        request = json.loads(lines[0])
        if request.get("protocol") != "olp-conformance-adapter-v1":
            raise ValueError("protocol mismatch")
        operation = request["operation"]
        adapter = ReferenceAdapter()
        if operation == "capabilities":
            output = {"capabilities": sorted(adapter.capabilities())}
        else:
            output = adapter.execute(operation, request.get("input", {}))
        response = {"protocol": "olp-conformance-adapter-v1", "ok": True, "output": output}
    except AdapterExecutionError as exc:
        response = {
            "protocol": "olp-conformance-adapter-v1",
            "ok": False,
            "error": {"classification": exc.classification, "reason": exc.reason, "message": exc.message},
        }
    except Exception as exc:
        response = {
            "protocol": "olp-conformance-adapter-v1",
            "ok": False,
            "error": {"classification": "ERROR", "reason": type(exc).__name__, "message": str(exc)},
        }
    print(json.dumps(response, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
