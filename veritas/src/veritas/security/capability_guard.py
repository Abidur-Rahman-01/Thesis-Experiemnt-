"""AgentDojo-style Provenance and Capability Enforcement Guard.

Prevents prompt injections, untrusted tool output taint, and unauthorized
privilege escalations from mutating state or leaking confidential resources.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from veritas.actions.contracts import ActionContract


INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"curl\s+.*?\|\s*(?:bash|sh)", re.IGNORECASE),
    re.compile(r"wget\s+.*?\|\s*(?:bash|sh)", re.IGNORECASE),
    re.compile(r"rm\s+-rf\s+/", re.IGNORECASE),
)


@dataclass(frozen=True)
class SecurityViolation:
    action_id: str
    reason: str
    taint_source: str
    severity: str = "high"


@dataclass(frozen=True)
class CapabilityGuard:
    """Enforces capability boundaries and taint isolation on action contracts."""

    allow_untrusted_mutations: bool = False
    strict_injection_checks: bool = True

    def check(self, contract: ActionContract) -> tuple[bool, SecurityViolation | None]:
        """Inspect an action contract for security policy or taint violations."""
        # 1. Capability Boundary: Untrusted observations cannot escalate to state-mutating actions
        if contract.provenance.has_untrusted and not self.allow_untrusted_mutations:
            if contract.mutates_state or any(
                p.startswith(("workspace:write", "admin:", "secret:", "external:", "network:"))
                for p in contract.permissions_required
            ):
                return False, SecurityViolation(
                    action_id=contract.action_id,
                    reason="Untrusted observation source attempted to invoke state-mutating or privileged action",
                    taint_source="untrusted_input",
                    severity="critical",
                )

        # 2. Adversarial Prompt Injection Signatures in arguments / intent
        if self.strict_injection_checks:
            text = f"{contract.intent} {contract.operation} {contract.arguments}"
            for pattern in INJECTION_PATTERNS:
                if pattern.search(text):
                    return False, SecurityViolation(
                        action_id=contract.action_id,
                        reason=f"Detected adversarial prompt injection or destructive pattern matching: {pattern.pattern}",
                        taint_source="adversarial_payload",
                        severity="high",
                    )

        # 3. Secret Exfiltration / Privilege Escalation Guard
        if contract.provenance.has_secret and "network:" in " ".join(contract.permissions_required).lower():
            return False, SecurityViolation(
                action_id=contract.action_id,
                reason="Action contains secret data and requests network exfiltration permissions",
                taint_source="secret_taint",
                severity="critical",
            )

        return True, None
