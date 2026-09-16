"""Termination checks."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.core.state import RunState


@dataclass(frozen=True)
class TerminationPolicy:
    max_steps: int = 40

    def should_stop(self, state: RunState) -> bool:
        return state.termination_status != "running" or state.step_index >= self.max_steps
