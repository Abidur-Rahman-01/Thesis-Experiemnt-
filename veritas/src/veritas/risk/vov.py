"""Risk-Calibrated Value-of-Verification."""

from __future__ import annotations

from dataclasses import dataclass


EPS = 1e-9


@dataclass(frozen=True)
class VovInputs:
    p_error: float
    impact: float
    detection_rate: float
    false_positive_rate: float
    residual_loss_after_recovery: float
    verification_cost: float
    false_positive_cost: float = 0.1


@dataclass(frozen=True)
class VovResult:
    delta: float
    marginal_value: float
    no_verify_loss: float
    verify_loss: float


def compute_vov(inputs: VovInputs) -> VovResult:
    p_error = _clip01(inputs.p_error)
    impact = _clip01(inputs.impact)
    detection_rate = _clip01(inputs.detection_rate)
    false_positive_rate = _clip01(inputs.false_positive_rate)
    rho = _clip01(inputs.residual_loss_after_recovery)
    verification_cost = max(0.0, inputs.verification_cost)
    false_positive_cost = max(0.0, inputs.false_positive_cost)

    no_verify_loss = p_error * impact
    verify_loss = (
        verification_cost
        + p_error * ((1.0 - detection_rate) * impact + detection_rate * rho * impact)
        + (1.0 - p_error) * false_positive_rate * false_positive_cost
    )
    delta = no_verify_loss - verify_loss
    marginal_value = max(delta, 0.0) / (verification_cost + EPS)
    return VovResult(delta=delta, marginal_value=marginal_value, no_verify_loss=no_verify_loss, verify_loss=verify_loss)


@dataclass(frozen=True)
class GateDecision:
    selected: bool
    reason: str
    threshold: float
    vov: VovResult


@dataclass(frozen=True)
class BudgetController:
    lambda0: float = 0.0
    kappa: float = 1.0

    def threshold(self, remaining: float, total: float) -> float:
        if total <= 0:
            return float("inf")
        consumed_fraction = 1.0 - max(0.0, remaining) / total
        return self.lambda0 * (1.0 + self.kappa * consumed_fraction)

    def choose(self, vov: VovResult, *, cost: float, remaining: float, total: float, hard_critical: bool = False) -> GateDecision:
        threshold = self.threshold(remaining, total)
        if cost > remaining:
            return GateDecision(False, "insufficient_budget", threshold, vov)
        if hard_critical:
            return GateDecision(True, "hard_critical", threshold, vov)
        if vov.marginal_value >= threshold and vov.delta > 0:
            return GateDecision(True, "positive_value", threshold, vov)
        return GateDecision(False, "below_threshold", threshold, vov)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
