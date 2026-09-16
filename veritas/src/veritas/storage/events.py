"""JSONL event storage for reproducible action logs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from veritas.core.state import ActionEvent


@dataclass
class JSONLEventStore:
    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: ActionEvent | dict) -> None:
        payload = event.to_dict() if hasattr(event, "to_dict") else dict(event)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def extend(self, events: Iterable[ActionEvent | dict]) -> None:
        for event in events:
            self.append(event)

    def read_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        records: list[dict] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records
