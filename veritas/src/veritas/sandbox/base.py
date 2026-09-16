"""Local sandbox interface and a safe toy implementation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from veritas.actions.contracts import ActionContract
from veritas.sandbox.checkpoint import DirectoryCheckpointStore, FilesystemCheckpoint
from veritas.sandbox.resource_limits import ResourceLimits


@dataclass(frozen=True)
class ExecutionResult:
    ok: bool
    output: str = ""
    error: str = ""
    return_code: int = 0


class Sandbox(Protocol):
    def checkpoint(self) -> FilesystemCheckpoint: ...

    def restore(self, checkpoint: FilesystemCheckpoint) -> str: ...

    def execute(self, action: ActionContract) -> ExecutionResult: ...


@dataclass
class LocalWorkspaceSandbox:
    workspace: Path
    limits: ResourceLimits = ResourceLimits()

    def __post_init__(self) -> None:
        self.workspace = Path(self.workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.checkpoints = DirectoryCheckpointStore(self.workspace)

    def checkpoint(self) -> FilesystemCheckpoint:
        return self.checkpoints.checkpoint()

    def restore(self, checkpoint: FilesystemCheckpoint) -> str:
        return self.checkpoints.restore(checkpoint)

    def execute(self, action: ActionContract) -> ExecutionResult:
        if action.tool == "fs":
            return self._execute_fs(action)
        if action.tool == "shell.exec":
            return self._execute_shell(action)
        return ExecutionResult(False, error=f"unsupported tool: {action.tool}", return_code=2)

    def _resolve(self, raw_path: str) -> Path:
        candidate = (self.workspace / raw_path).resolve()
        workspace = self.workspace.resolve()
        if candidate != workspace and workspace not in candidate.parents:
            raise ValueError("path escapes workspace")
        return candidate

    def _execute_fs(self, action: ActionContract) -> ExecutionResult:
        try:
            operation = action.operation
            path = self._resolve(str(action.arguments.get("path", "")))
            workspace = self.workspace.resolve()
            if operation == "read":
                return ExecutionResult(True, output=path.read_text(encoding="utf-8"))
            if operation in {"write", "append"}:
                path.parent.mkdir(parents=True, exist_ok=True)
                mode = "a" if operation == "append" else "w"
                with path.open(mode, encoding="utf-8") as handle:
                    handle.write(str(action.arguments.get("content", "")))
                return ExecutionResult(True, output=str(path.relative_to(workspace)))
            if operation == "delete":
                if path.is_dir():
                    return ExecutionResult(False, error="directory delete is blocked in local toy sandbox", return_code=3)
                path.unlink(missing_ok=True)
                return ExecutionResult(True, output=str(path.relative_to(workspace)))
        except Exception as exc:  # noqa: BLE001 - sandbox boundary converts exceptions to result.
            return ExecutionResult(False, error=str(exc), return_code=1)
        return ExecutionResult(False, error=f"unsupported fs operation: {action.operation}", return_code=2)

    def _execute_shell(self, action: ActionContract) -> ExecutionResult:
        command = action.arguments.get("command")
        if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
            return ExecutionResult(False, error="shell.exec requires command as a list of strings", return_code=2)
        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=self.limits.timeout_seconds,
                check=False,
            )
            output = (completed.stdout + completed.stderr)[: self.limits.max_output_bytes]
            return ExecutionResult(completed.returncode == 0, output=output, return_code=completed.returncode)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            return ExecutionResult(False, output=stdout, error="sandbox command timed out", return_code=124)
        except OSError as exc:
            return ExecutionResult(False, error=f"could not start command: {exc}", return_code=127)
