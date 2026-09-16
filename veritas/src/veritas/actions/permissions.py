"""Permission and capability validation for action contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.actions.contracts import ActionContract, ContractValidation, validate_schema


@dataclass(frozen=True)
class PermissionPolicy:
    granted_permissions: frozenset[str] = field(default_factory=lambda: frozenset({"workspace:read"}))
    allowed_tools: frozenset[str] | None = None
    block_untrusted_privilege_escalation: bool = True

    def validate(self, contract: ActionContract) -> ContractValidation:
        reasons: list[str] = []
        schema = validate_schema(contract)
        reasons.extend(schema.reasons)

        if self.allowed_tools is not None and contract.tool not in self.allowed_tools:
            reasons.append(f"tool not allowed: {contract.tool}")

        missing = set(contract.permissions_required) - set(self.granted_permissions)
        if missing:
            reasons.append(f"missing permissions: {', '.join(sorted(missing))}")

        privileged = any(
            permission.startswith(("network:", "secret:", "external:", "admin:"))
            for permission in contract.permissions_required
        )
        if self.block_untrusted_privilege_escalation and contract.provenance.has_untrusted and privileged:
            reasons.append("untrusted content cannot authorize privileged action")

        return ContractValidation.fail(*reasons) if reasons else ContractValidation.pass_()
