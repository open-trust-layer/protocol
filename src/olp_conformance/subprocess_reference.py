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
from .strict_json import MAX_JSON_BYTES, StrictJSONError, loads as strict_json_loads


def _malformed(reason: str, message: str) -> dict[str, object]:
    return {
        "protocol": "olp-conformance-adapter-v1",
        "ok": False,
        "error": {"classification": "MALFORMED", "reason": reason, "message": message},
    }


def main() -> int:
    raw = sys.stdin.buffer.read(MAX_JSON_BYTES + 2)
    if len(raw) > MAX_JSON_BYTES + 1:
        print(json.dumps(_malformed("REQUEST_TOO_LARGE", "request exceeds adapter size limit"), separators=(",", ":"), sort_keys=True))
        return 0
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        print(json.dumps(_malformed("INVALID_JSON", "request is not valid UTF-8"), separators=(",", ":"), sort_keys=True))
        return 0

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) != 1:
        print(json.dumps(_malformed("REQUEST_COUNT", "expected exactly one request"), separators=(",", ":"), sort_keys=True))
        return 0
    try:
        request = strict_json_loads(lines[0])
        if not isinstance(request, dict):
            raise StrictJSONError("request MUST be a JSON object")
        if request.get("protocol") != "olp-conformance-adapter-v1":
            raise StrictJSONError("protocol mismatch")
        operation = request["operation"]
        if not isinstance(operation, str):
            raise StrictJSONError("operation MUST be a string")
        adapter = ReferenceAdapter()
        if operation == "capabilities":
            output = {"capabilities": sorted(adapter.capabilities())}
        else:
            input_value = request.get("input", {})
            if not isinstance(input_value, dict):
                raise StrictJSONError("input MUST be an object")
            output = adapter.execute(operation, input_value)
        response = {"protocol": "olp-conformance-adapter-v1", "ok": True, "output": output}
    except StrictJSONError as exc:
        response = _malformed("INVALID_JSON", str(exc))
    except AdapterExecutionError as exc:
        response = {
            "protocol": "olp-conformance-adapter-v1",
            "ok": False,
            "error": {"classification": exc.classification, "reason": exc.reason, "message": exc.message},
        }
    except (KeyError, TypeError, ValueError) as exc:
        response = _malformed("MALFORMED_REQUEST", str(exc))
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
