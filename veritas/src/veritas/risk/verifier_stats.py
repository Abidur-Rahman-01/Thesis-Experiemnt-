"""Class-level verifier operating statistics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VerifierClassStats:
    detection_rate: float
    false_positive_rate: float
    error_count: int = 0
    correct_count: int = 0

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "VerifierClassStats":
        return cls(
            detection_rate=float(data.get("detection_rate", 0.5)),
            false_positive_rate=float(data.get("false_positive_rate", 0.1)),
            error_count=int(data.get("error_count", 0)),
            correct_count=int(data.get("correct_count", 0)),
        )


@dataclass(frozen=True)
class VerifierStatsTable:
    by_class: dict[str, VerifierClassStats]
    default: VerifierClassStats = VerifierClassStats(0.5, 0.1)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "VerifierStatsTable":
        default = VerifierClassStats.from_mapping(data.get("default", {}))
        by_class = {
            name: VerifierClassStats.from_mapping(value)
            for name, value in data.items()
            if isinstance(value, dict) and name != "default"
        }
        return cls(by_class=by_class, default=default)

    @classmethod
    def from_json(cls, path: str | Path) -> "VerifierStatsTable":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_mapping(json.load(handle))

    def for_class(self, action_class: str) -> VerifierClassStats:
        return self.by_class.get(action_class, self.default)
