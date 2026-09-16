"""Class-level recovery residual-loss statistics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RecoveryClassStats:
    residual_loss: float
    trials: int = 0
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RecoveryClassStats":
        return cls(
            residual_loss=float(data.get("residual_loss", 0.5)),
            trials=int(data.get("trials", 0)),
            notes=str(data.get("notes", "")),
        )


@dataclass(frozen=True)
class RecoveryStatsTable:
    by_class: dict[str, RecoveryClassStats]
    default: RecoveryClassStats = RecoveryClassStats(0.5)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RecoveryStatsTable":
        default = RecoveryClassStats.from_mapping(data.get("default", {}))
        by_class = {
            name: RecoveryClassStats.from_mapping(value)
            for name, value in data.items()
            if isinstance(value, dict) and name != "default"
        }
        return cls(by_class=by_class, default=default)

    @classmethod
    def from_json(cls, path: str | Path) -> "RecoveryStatsTable":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_mapping(json.load(handle))

    def for_class(self, action_class: str) -> RecoveryClassStats:
        return self.by_class.get(action_class, self.default)
