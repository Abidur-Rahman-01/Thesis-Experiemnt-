"""Budget accounting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VerificationBudget:
    total: float
    remaining: float | None = None
    unit: str = "normalized_cost"

    def __post_init__(self) -> None:
        if self.remaining is None:
            self.remaining = self.total
        if self.total < 0 or self.remaining < 0:
            raise ValueError("budget values must be non-negative")

    @property
    def spent(self) -> float:
        return self.total - float(self.remaining)

    @property
    def consumed_fraction(self) -> float:
        if self.total <= 0:
            return 1.0
        return min(1.0, max(0.0, self.spent / self.total))

    def can_spend(self, cost: float) -> bool:
        return cost <= float(self.remaining)

    def spend(self, cost: float) -> None:
        if cost < 0:
            raise ValueError("cannot spend negative budget")
        if cost > float(self.remaining):
            raise ValueError("verification budget exhausted")
        self.remaining = float(self.remaining) - cost
