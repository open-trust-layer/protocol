"""Implementation-neutral conformance adapter interfaces.

The harness can drive an in-process Python adapter or any external executable
that implements the JSON-lines request/response contract documented in
``conformance/README.md``.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .strict_json import MAX_JSON_BYTES, loads as strict_json_loads


@dataclass(slots=True)
class AdapterExecutionError(Exception):
    classification: str
    reason: str
    message: str

    def __str__(self) -> str:
        return f"{self.classification}/{self.reason}: {self.message}"


@runtime_checkable
class ConformanceAdapter(Protocol):
    @property
    def name(self) -> str: ...

    def capabilities(self) -> frozenset[str]: ...

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]: ...


class SubprocessAdapter:
    """Drive a language-neutral executable using one JSON request per process.

    A one-process-per-case model is intentionally conservative for v1: it makes
    test isolation deterministic and prevents one malformed vector from poisoning
    later cases. Future harness versions may add a persistent transport profile.
    """

    def __init__(self, command: str | list[str], *, timeout: float = 10.0, name: str | None = None, env: dict[str, str] | None = None) -> None:
        self._command = shlex.split(command) if isinstance(command, str) else list(command)
        if not self._command:
            raise ValueError("subprocess adapter command cannot be empty")
        self._timeout = timeout
        self._name = name or "subprocess:" + self._command[0]
        self._env = dict(env or {})
        self._capabilities: frozenset[str] | None = None

    @property
    def name(self) -> str:
        return self._name

    def capabilities(self) -> frozenset[str]:
        if self._capabilities is None:
            response = self._invoke({"protocol": "olp-conformance-adapter-v1", "operation": "capabilities", "input": {}})
            caps = response.get("output", {}).get("capabilities")
            if not isinstance(caps, list) or not all(isinstance(item, str) for item in caps):
                raise RuntimeError("subprocess adapter returned invalid capabilities response")
            self._capabilities = frozenset(caps)
        return self._capabilities

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._invoke(
            {"protocol": "olp-conformance-adapter-v1", "operation": operation, "input": payload}
        )
        if response.get("ok") is True:
            output = response.get("output")
            if not isinstance(output, dict):
                raise RuntimeError("subprocess adapter output MUST be an object")
            return output
        error = response.get("error") or {}
        raise AdapterExecutionError(
            classification=str(error.get("classification", "ERROR")),
            reason=str(error.get("reason", "ADAPTER_ERROR")),
            message=str(error.get("message", "adapter operation failed")),
        )

    def _invoke(self, request: dict[str, Any]) -> dict[str, Any]:
        try:
            completed = subprocess.run(
                self._command,
                input=json.dumps(request, separators=(",", ":")) + "\n",
                text=True,
                capture_output=True,
                timeout=self._timeout,
                check=False,
                env={**os.environ, **self._env},
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"failed to execute subprocess adapter: {exc}") from exc
        if completed.returncode != 0:
            raise RuntimeError(
                f"subprocess adapter exited {completed.returncode}: {completed.stderr.strip()}"
            )
        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        if len(lines) != 1:
            raise RuntimeError("subprocess adapter MUST emit exactly one JSON response line")
        if len(completed.stdout.encode("utf-8", "replace")) > MAX_JSON_BYTES:
            raise RuntimeError("subprocess adapter response exceeds size limit")
        response = strict_json_loads(lines[0])
        if not isinstance(response, dict):
            raise RuntimeError("subprocess adapter response MUST be an object")
        if response.get("protocol") != "olp-conformance-adapter-v1":
            raise RuntimeError("subprocess adapter response protocol mismatch")
        return response
