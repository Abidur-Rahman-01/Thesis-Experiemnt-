"""Offline matched-budget replay over logged action records."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.eval.baselines import RandomBudgetMatchedScheduler, Scheduler, record_cost


@dataclass(frozen=True)
class ReplayResult:
    policy_name: str
    budget: float
    selected_action_ids: tuple[str, ...]
    selected_count: int
    verification_cost: float
    errors_caught: int
    consequential_errors_caught: int
    false_rejections: int
    budget_exhausted: bool
    allocation_metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "policy_name": self.policy_name,
            "budget": self.budget,
            "selected_action_ids": list(self.selected_action_ids),
            "selected_count": self.selected_count,
            "verification_cost": self.verification_cost,
            "errors_caught": self.errors_caught,
            "consequential_errors_caught": self.consequential_errors_caught,
            "false_rejections": self.false_rejections,
            "budget_exhausted": self.budget_exhausted,
            "allocation_metrics": self.allocation_metrics,
        }


@dataclass(frozen=True)
class ReplayEngine:
    records: tuple[dict, ...]
    consequential_impact_threshold: float = 0.5

    def run(self, scheduler: Scheduler, *, budget: float) -> ReplayResult:
        remaining = budget
        selected_ids: list[str] = []
        errors_caught = 0
        consequential_errors_caught = 0
        false_rejections = 0

        records = self.records
        if isinstance(scheduler, RandomBudgetMatchedScheduler):
            records = tuple(sorted(records, key=scheduler.priority))

        for record in records:
            decision = scheduler.select(record, remaining_budget=remaining, total_budget=budget)
            if not decision.selected:
                continue
            cost = record_cost(record)
            if cost > remaining:
                continue
            remaining -= cost
            selected_ids.append(str(record.get("action_id", record.get("action_json", {}).get("action_id", ""))))

            label = str(record.get("ground_truth_label", "unresolved"))
            verdict = str(record.get("verifier_verdict", "pass"))
            if label == "error" and verdict in {"fail", "uncertain"}:
                errors_caught += 1
                if float(record.get("impact", 0.0)) >= self.consequential_impact_threshold:
                    consequential_errors_caught += 1
            if label == "correct" and verdict == "fail":
                false_rejections += 1

        spent = budget - remaining
        selected_count = len(selected_ids)
        precision = errors_caught / selected_count if selected_count else 0.0
        consequential_precision = consequential_errors_caught / selected_count if selected_count else 0.0
        return ReplayResult(
            policy_name=scheduler.name,
            budget=budget,
            selected_action_ids=tuple(selected_ids),
            selected_count=selected_count,
            verification_cost=spent,
            errors_caught=errors_caught,
            consequential_errors_caught=consequential_errors_caught,
            false_rejections=false_rejections,
            budget_exhausted=remaining <= 1e-9,
            allocation_metrics={
                "precision": precision,
                "consequential_precision": consequential_precision,
                "budget_remaining": remaining,
            },
        )

    def sweep(self, schedulers: list[Scheduler], budgets: list[float]) -> list[ReplayResult]:
        return [self.run(scheduler, budget=budget) for scheduler in schedulers for budget in budgets]
