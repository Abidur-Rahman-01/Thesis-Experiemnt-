"""Critical-Step Optimization (CSO) Harvester.

Mines verified, outcome-changing recovery branches into (prompt, chosen, rejected)
preference pairs for Direct Preference Optimization (DPO) and parameter-efficient post-training.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from veritas.recovery.branches import RecoveryBranch


@dataclass
class CSOHarvester:
    """Harvests recovery branches into DPO preference data."""

    branches: list[RecoveryBranch] = field(default_factory=list)

    def record_branch(
        self,
        *,
        branch_id: str,
        parent_step: int,
        failed_action_id: str,
        alternative_action_id: str | None = None,
        outcome: str = "success",
        prompt: str = "",
        failed_action_contract: dict | None = None,
        alternative_action_contract: dict | None = None,
        vov_delta: float = 0.0,
        cost_saved: float = 0.0,
    ) -> RecoveryBranch:
        branch = RecoveryBranch(
            branch_id=branch_id,
            parent_step=parent_step,
            failed_action_id=failed_action_id,
            alternative_action_id=alternative_action_id,
            outcome=outcome,
            prompt=prompt,
            failed_action_contract=failed_action_contract,
            alternative_action_contract=alternative_action_contract,
            vov_delta=vov_delta,
            cost_saved=cost_saved,
        )
        self.branches.append(branch)
        return branch

    def harvest_dpo_pairs(self) -> list[dict[str, Any]]:
        """Extract valid (chosen, rejected) preference pairs from successful recovery branches."""
        pairs = []
        for branch in self.branches:
            pair = branch.to_dpo_pair()
            if pair is not None:
                pairs.append(pair)
        return pairs

    def export_jsonl(self, output_path: str | Path, *, append: bool = False) -> int:
        """Export harvested preference pairs to JSONL formatted for DPO / HuggingFace TRL."""
        pairs = self.harvest_dpo_pairs()
        dest = Path(output_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with dest.open(mode, encoding="utf-8") as f:
            for pair in pairs:
                f.write(json.dumps(pair, sort_keys=True) + "\n")
        return len(pairs)
