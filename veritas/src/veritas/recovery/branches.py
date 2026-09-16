"""Recovery branch records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryBranch:
    branch_id: str
    parent_step: int
    failed_action_id: str
    alternative_action_id: str | None = None
    outcome: str = "unresolved"
