"""Model-facing protocols used by the runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from veritas.actions.contracts import ActionContract


@dataclass(frozen=True)
class ErrorEstimate:
    raw_score: float
    score_is_probability: bool = False
    rationale: str = ""


class PolicyModel(Protocol):
    def propose_action(self, context: "PolicyContext") -> ActionContract | None:
        """Return the next proposed action, or None when the policy is done."""


class ErrorEstimator(Protocol):
    def estimate(self, context: "PolicyContext", action: ActionContract) -> ErrorEstimate:
        """Return a raw error score or logit for the proposed action."""


@dataclass(frozen=True)
class PolicyContext:
    goal: str
    step_index: int
    history: tuple[dict, ...]
