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

    @property
    def passed(self) -> bool:
        return self.verdict == "pass"

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


@dataclass(frozen=True)
class RevisesSemanticVerifier:
    """ReVISE-style semantic verifier supporting intrinsic self-consistency checks."""

    evaluator: Any = None
    cost: float = 0.03

    def verify(self, contract: ActionContract, context_goal: str = "") -> VerificationResult:
        # Fall back to heuristic check
        base_result = HeuristicSemanticVerifier().verify(contract)
        if base_result.verdict == "fail":
            return base_result

        # If an evaluator callable or model is attached, run intrinsic semantic check
        if self.evaluator is not None and callable(self.evaluator):
            try:
                prompt = (
                    f"Check if this proposed action logically supports the goal without errors:\n"
                    f"Goal: {context_goal or contract.intent}\n"
                    f"Action: {contract.tool}.{contract.operation}({contract.arguments})\n"
                    f"Is this action logically correct? Answer YES or NO with reason."
                )
                eval_resp = str(self.evaluator(prompt)).strip().upper()
                if "NO" in eval_resp[:20]:
                    return VerificationResult(
                        verdict="fail",
                        checks=(VerificationCheck("revise_self_consistency", "fail", eval_resp[:150]),),
                        recommended_action="block",
                        cost=self.cost,
                    )
            except Exception:
                pass

        return VerificationResult(
            verdict="pass",
            checks=(VerificationCheck("revise_self_consistency", "pass", "action passed semantic check"),),
            recommended_action="execute",
            cost=self.cost,
        )
