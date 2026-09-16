"""Semantic verification result types and a deterministic heuristic verifier."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.actions.contracts import ActionContract


@dataclass(frozen=True)
class VerificationCheck:
    type: str
    status: str
    message: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type, "status": self.status, "message": self.message}


@dataclass(frozen=True)
class VerificationResult:
    verdict: str
    checks: tuple[VerificationCheck, ...] = ()
    estimated_error_probability: float | None = None
    recommended_action: str = "execute"
    cost: float = 0.03

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "checks": [check.to_dict() for check in self.checks],
            "estimated_error_probability": self.estimated_error_probability,
            "recommended_action": self.recommended_action,
            "cost": self.cost,
        }


@dataclass(frozen=True)
class HeuristicSemanticVerifier:
    """Cheap deterministic stand-in for a future semantic verifier model."""

    def verify(self, contract: ActionContract) -> VerificationResult:
        checks: list[VerificationCheck] = []
        text = " ".join([contract.tool, contract.operation, str(contract.arguments), contract.intent]).lower()

        if "rm -rf /" in text or "delete root" in text:
            checks.append(VerificationCheck("semantic", "fail", "destructive root deletion pattern"))
        if contract.provenance.has_untrusted and any(prefix.startswith(("network:", "secret:", "external:")) for prefix in contract.permissions_required):
            checks.append(VerificationCheck("semantic", "fail", "untrusted data requests privileged authority"))
        if "known_bad" in text or "expected_fail" in text:
            checks.append(VerificationCheck("semantic", "fail", "contract contains explicit bad-action marker"))

        if checks:
            return VerificationResult(verdict="fail", checks=tuple(checks), recommended_action="block")
        return VerificationResult(verdict="pass", checks=(VerificationCheck("semantic", "pass", "no heuristic counterexample"),))
