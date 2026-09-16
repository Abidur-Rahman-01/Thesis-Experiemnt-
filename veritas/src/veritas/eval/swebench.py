"""SWE-bench manifest types.

This module intentionally does not download benchmark data. Paper 1 configs
should reference frozen task manifests produced outside the runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SwebenchTask:
    task_id: str
    repository: str
    base_commit: str | None = None
    issue: str | None = None


def load_task_manifest(path: str | Path) -> list[SwebenchTask]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [SwebenchTask(**item) for item in payload.get("tasks", [])]
