"""Deterministic action checks that run before expensive verification."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.actions.contracts import ActionContract
from veritas.actions.permissions import PermissionPolicy
from veritas.security.capability_guard import CapabilityGuard
from veritas.verification.semantic import VerificationCheck, VerificationResult


@dataclass(frozen=True)
class DeterministicVerifier:
    permission_policy: PermissionPolicy
    capability_guard: CapabilityGuard = field(default_factory=CapabilityGuard)

    def verify(self, contract: ActionContract) -> VerificationResult:
        checks: list[VerificationCheck] = []

        # 1. Schema & Permission Policy Validation
        validation = self.permission_policy.validate(contract)
        if validation.allowed:
            checks.append(VerificationCheck("schema_permission", "pass", "schema and permissions accepted"))
        else:
            for reason in validation.reasons:
                checks.append(VerificationCheck("schema_permission", "fail", reason))

        # 2. AgentDojo Capability & Security Guard
        allowed, violation = self.capability_guard.check(contract)
        if not allowed and violation is not None:
            checks.append(VerificationCheck("security_capability", "fail", f"[{violation.severity}] {violation.reason}"))

        # 3. Path Traversal Invariant
        path = str(contract.arguments.get("path", ""))
        if path.startswith("/") or ".." in path.split("/"):
            checks.append(VerificationCheck("resource_scope", "fail", "path must stay inside workspace"))

        # 4. POPPER Invariant & Precondition Assertions
        for pre in contract.preconditions:
            if "must_exist" in pre and not contract.resources:
                checks.append(VerificationCheck("popper_invariant", "fail", f"Precondition violated: {pre}"))

        # 5. Arithmetic & Syntax Invariants (for math and calculation actions)
        if "calc" in contract.tool or "math" in contract.tool:
            expr = str(contract.arguments.get("expression", ""))
            if "/ 0" in expr or "/0" in expr:
                checks.append(VerificationCheck("popper_invariant", "fail", "ZeroDivisionError invariant violation"))

        verdict = "fail" if any(check.status == "fail" for check in checks) else "pass"
        return VerificationResult(
            verdict=verdict,
            checks=tuple(checks),
            recommended_action="block" if verdict == "fail" else "execute",
            cost=0.0,
        )
