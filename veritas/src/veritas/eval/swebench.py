"""SWE-bench manifest validation and mini-SWE-agent command construction."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SwebenchTask:
    task_id: str
    repository: str
    base_commit: str | None = None
    issue: str | None = None


@dataclass(frozen=True)
class SwebenchManifest:
    dataset: str
    split: str
    frozen: bool
    tasks: tuple[SwebenchTask, ...]
    source_revision: str | None = None

    def validate(self, *, require_frozen: bool = True) -> None:
        if require_frozen and not self.frozen:
            raise ValueError("SWE-bench manifest is not frozen")
        if not self.tasks:
            raise ValueError("SWE-bench manifest contains no tasks")
        ids = [task.task_id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("SWE-bench manifest contains duplicate task IDs")
        if any(not task_id.strip() for task_id in ids):
            raise ValueError("SWE-bench task IDs must be non-empty")


def load_task_manifest(path: str | Path) -> list[SwebenchTask]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [SwebenchTask(**item) for item in payload.get("tasks", [])]


def load_manifest(path: str | Path) -> SwebenchManifest:
    """Load the frozen JSON manifest used to define an experimental slice."""
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return SwebenchManifest(
        dataset=str(payload.get("dataset", "verified")),
        split=str(payload.get("split", "test")),
        frozen=bool(payload.get("frozen", False)),
        source_revision=payload.get("source_revision"),
        tasks=tuple(SwebenchTask(**item) for item in payload.get("tasks", [])),
    )


def build_minisweagent_command(
    manifest: SwebenchManifest,
    *,
    mini_swe_root: str | Path,
    output_dir: str | Path,
    model: str,
    workers: int = 1,
) -> list[str]:
    """Construct a batch command without importing mini-SWE-agent internals."""
    manifest.validate()
    if workers < 1:
        raise ValueError("workers must be at least 1")
    escaped_ids = "|".join(re.escape(task.task_id) for task in manifest.tasks)
    module_root = Path(mini_swe_root).resolve() / "src"
    return [
        sys.executable,
        "-m",
        "minisweagent.run.benchmarks.swebench",
        "--subset",
        manifest.dataset,
        "--split",
        manifest.split,
        "--filter",
        f"^(?:{escaped_ids})$",
        "--output",
        str(Path(output_dir)),
        "--workers",
        str(workers),
        "--model",
        model,
        "--environment-class",
        "docker",
        "--config",
        str(module_root / "minisweagent" / "config" / "benchmarks" / "swebench.yaml"),
    ]
