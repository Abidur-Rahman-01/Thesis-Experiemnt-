"""Lightweight local estimators used for development and tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.actions.classes import ActionClass
from veritas.actions.contracts import ActionContract
from veritas.models.base import ErrorEstimate, PolicyContext
from veritas.risk.calibrator import logit
from veritas.risk.impact import ImpactModel


@dataclass(frozen=True)
class HeuristicErrorEstimator:
    """A deterministic pilot estimator, not a publication-grade model."""

    impact_model: ImpactModel = field(default_factory=ImpactModel)

    def estimate(self, context: PolicyContext, action: ActionContract) -> ErrorEstimate:
        impact = self.impact_model.score(action).value
        action_class = action.action_class
        probability = 0.08 + 0.55 * impact

        if action_class in {ActionClass.DESTRUCTIVE_FILESYSTEM, ActionClass.EXTERNAL_MUTATION}:
            probability += 0.15
        if action.provenance.has_untrusted:
            probability += 0.10
        if "fail" in action.intent.lower() or "bad" in action.intent.lower():
            probability += 0.20

        probability = max(0.01, min(0.99, probability))
        return ErrorEstimate(raw_score=logit(probability), score_is_probability=False, rationale="heuristic pilot score")
