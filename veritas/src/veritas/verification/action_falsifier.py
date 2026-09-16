"""Action falsification pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.contracts import ActionContract
from veritas.verification.deterministic import DeterministicVerifier
from veritas.verification.semantic import HeuristicSemanticVerifier, VerificationResult


@dataclass(frozen=True)
class ActionFalsifier:
    deterministic: DeterministicVerifier
    semantic: HeuristicSemanticVerifier = HeuristicSemanticVerifier()

    def verify(self, contract: ActionContract) -> VerificationResult:
        deterministic = self.deterministic.verify(contract)
        if deterministic.verdict == "fail":
            return deterministic

        semantic = self.semantic.verify(contract)
        checks = deterministic.checks + semantic.checks
        verdict = semantic.verdict
        return VerificationResult(
            verdict=verdict,
            checks=checks,
            estimated_error_probability=semantic.estimated_error_probability,
            recommended_action=semantic.recommended_action,
            cost=deterministic.cost + semantic.cost,
        )
