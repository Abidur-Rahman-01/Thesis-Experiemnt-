"""Verifier model wrappers."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.contracts import ActionContract
from veritas.models.base import PolicyContext
from veritas.verification.action_falsifier import ActionFalsifier
from veritas.verification.semantic import VerificationResult


@dataclass(frozen=True)
class HeuristicVerifier:
    falsifier: ActionFalsifier

    def verify(self, context: PolicyContext, action: ActionContract) -> VerificationResult:
        return self.falsifier.verify(action)
