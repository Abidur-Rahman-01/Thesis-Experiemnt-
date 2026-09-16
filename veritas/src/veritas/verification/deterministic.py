"""Deterministic action checks that run before expensive verification."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.contracts import ActionContract
from veritas.actions.permissions import PermissionPolicy
from veritas.verification.semantic import VerificationCheck, VerificationResult


@dataclass(frozen=True)
class DeterministicVerifier:
    permission_policy: PermissionPolicy

    def verify(self, contract: ActionContract) -> VerificationResult:
        validation = self.permission_policy.validate(contract)
        checks: list[VerificationCheck] = []
        if validation.allowed:
            checks.append(VerificationCheck("schema_permission", "pass", "schema and permissions accepted"))
        else:
            for reason in validation.reasons:
                checks.append(VerificationCheck("schema_permission", "fail", reason))

        path = str(contract.arguments.get("path", ""))
        if path.startswith("/") or ".." in path.split("/"):
            checks.append(VerificationCheck("resource_scope", "fail", "path must stay inside workspace"))

        verdict = "fail" if any(check.status == "fail" for check in checks) else "pass"
        return VerificationResult(verdict=verdict, checks=tuple(checks), recommended_action="block" if verdict == "fail" else "execute")
