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
    prompt: str = ""
    failed_action_contract: dict | None = None
    alternative_action_contract: dict | None = None
    vov_delta: float = 0.0
    cost_saved: float = 0.0

    def to_dpo_pair(self) -> dict | None:
        """Convert a successful recovery branch into a (chosen, rejected) preference pair."""
        if self.outcome != "success" or not self.alternative_action_contract or not self.failed_action_contract:
            return None
        return {
            "branch_id": self.branch_id,
            "prompt": self.prompt or str(self.failed_action_contract.get("intent", "")),
            "chosen": self.alternative_action_contract,
            "rejected": self.failed_action_contract,
            "vov_delta": self.vov_delta,
            "cost_saved": self.cost_saved,
        }
