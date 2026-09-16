"""Runtime state and replayable action events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from veritas.actions.contracts import ActionContract
from veritas.core.budgets import VerificationBudget


@dataclass(frozen=True)
class CheckpointRecord:
    checkpoint_id: str
    step: int
    state_hash: str
    path: str


@dataclass(frozen=True)
class ActionEvent:
    run_id: str
    step: int
    action: ActionContract
    action_class: str
    raw_error_score: float
    calibrated_error_probability: float
    impact: float
    detection_rate_estimate: float
    false_positive_rate_estimate: float
    residual_loss_after_recovery: float
    estimated_cost: float
    delta_value: float
    selected: bool
    hard_critical: bool
    gate_reason: str
    verifier_verdict: str | None = None
    ground_truth_label: str = "unresolved"
    label_source: str = "unlabeled"
    executed: bool = False
    execution_success: bool | None = None
    checkpoint_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "step": self.step,
            "action_id": self.action.action_id,
            "action_json": self.action.to_dict(),
            "action_class": self.action_class,
            "raw_error_score": self.raw_error_score,
            "calibrated_error_probability": self.calibrated_error_probability,
            "impact": self.impact,
            "detection_rate_estimate": self.detection_rate_estimate,
            "false_positive_rate_estimate": self.false_positive_rate_estimate,
            "residual_loss_after_recovery": self.residual_loss_after_recovery,
            "estimated_cost": self.estimated_cost,
            "delta_value": self.delta_value,
            "selected": self.selected,
            "hard_critical": self.hard_critical,
            "gate_reason": self.gate_reason,
            "verifier_verdict": self.verifier_verdict,
            "ground_truth_label": self.ground_truth_label,
            "label_source": self.label_source,
            "executed": self.executed,
            "execution_success": self.execution_success,
            "checkpoint_id": self.checkpoint_id,
        }


@dataclass
class RunState:
    goal: str
    verification_budget: VerificationBudget
    run_id: str = field(default_factory=lambda: f"run_{uuid4().hex[:12]}")
    step_index: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    actions: list[ActionEvent] = field(default_factory=list)
    checkpoints: list[CheckpointRecord] = field(default_factory=list)
    termination_status: str = "running"

    def context_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.history)

    def record_action(self, event: ActionEvent) -> None:
        self.actions.append(event)
        self.history.append(event.to_dict())
        self.step_index += 1

    def record_checkpoint(self, checkpoint: CheckpointRecord) -> None:
        self.checkpoints.append(checkpoint)
