"""Counterfactual replanning interfaces."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.contracts import ActionContract


@dataclass(frozen=True)
class ReplanCandidate:
    action: ActionContract
    score: float
    rationale: str


class NoopReplanner:
    def propose(self, failed_action: ActionContract) -> list[ReplanCandidate]:
        return []
