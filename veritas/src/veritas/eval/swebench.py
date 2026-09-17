"""SWE-bench manifest validation and mini-SWE-agent command construction."""

from __future__ import annotations

import json
import hashlib
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
    stage: str | None = None
    selection_seed: int | None = None
    source_sha256: str | None = None

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
        stage=payload.get("stage"),
        selection_seed=payload.get("selection_seed"),
        source_sha256=payload.get("source_sha256"),
        tasks=tuple(SwebenchTask(**item) for item in payload.get("tasks", [])),
    )


def load_swebench_metadata(path: str | Path) -> tuple[list[SwebenchTask], str]:
    """Load exported SWE-bench JSON/JSONL metadata and return its content hash."""
    source = Path(path)
    raw = source.read_bytes()
    if source.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    else:
        payload = json.loads(raw)
        rows = payload.get("tasks", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("SWE-bench metadata must be a JSON list, JSONL records, or an object with tasks")

    tasks: list[SwebenchTask] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each SWE-bench metadata record must be an object")
        task_id = row.get("instance_id", row.get("task_id"))
        repository = row.get("repo", row.get("repository"))
        if not task_id or not repository:
            raise ValueError("each metadata record requires instance_id/task_id and repo/repository")
        tasks.append(
            SwebenchTask(
                task_id=str(task_id),
                repository=str(repository),
                base_commit=str(row["base_commit"]) if row.get("base_commit") else None,
                issue=str(row["problem_statement"]) if row.get("problem_statement") else row.get("issue"),
            )
        )
    if len({task.task_id for task in tasks}) != len(tasks):
        raise ValueError("SWE-bench metadata contains duplicate task IDs")
    return tasks, hashlib.sha256(raw).hexdigest()


def partition_tasks(
    tasks: list[SwebenchTask], stage_sizes: dict[str, int], *, seed: int
) -> dict[str, tuple[SwebenchTask, ...]]:
    """Create stable, non-overlapping partitions independent of source row order."""
    if not stage_sizes:
        raise ValueError("at least one stage size is required")
    if any(not name.strip() or size < 0 for name, size in stage_sizes.items()):
        raise ValueError("stage names must be non-empty and sizes must be non-negative")
    requested = sum(stage_sizes.values())
    if requested > len(tasks):
        raise ValueError(f"requested {requested} tasks but metadata contains only {len(tasks)}")
    ordered = sorted(
        tasks,
        key=lambda task: hashlib.sha256(f"{seed}:{task.task_id}".encode("utf-8")).hexdigest(),
    )
    partitions: dict[str, tuple[SwebenchTask, ...]] = {}
    offset = 0
    for stage, size in stage_sizes.items():
        partitions[stage] = tuple(ordered[offset : offset + size])
        offset += size
    return partitions


def manifest_payload(
    tasks: tuple[SwebenchTask, ...],
    *,
    stage: str,
    dataset: str,
    split: str,
    source_revision: str,
    source_sha256: str,
    seed: int,
) -> dict:
    return {
        "dataset": dataset,
        "split": split,
        "stage": stage,
        "frozen": True,
        "source_revision": source_revision,
        "source_sha256": source_sha256,
        "selection_seed": seed,
        "tasks": [
            {
                "task_id": task.task_id,
                "repository": task.repository,
                "base_commit": task.base_commit,
                "issue": task.issue,
            }
            for task in tasks
        ],
    }


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
