"""Typed action contracts.

The blueprint's central safety move is to stop executing free-form tool strings.
Every executable step becomes an inspectable contract first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from veritas.actions.classes import ActionClass, classify_action, is_state_mutating


TrustLabel = str


@dataclass(frozen=True)
class Provenance:
    argument_sources: tuple[TrustLabel, ...] = ("model_generated",)

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "Provenance":
        if not data:
            return cls()
        sources = data.get("argument_sources", ("model_generated",))
        return cls(argument_sources=tuple(str(source) for source in sources))

    def to_dict(self) -> dict[str, Any]:
        return {"argument_sources": list(self.argument_sources)}

    @property
    def has_untrusted(self) -> bool:
        return any("untrusted" in source.lower() for source in self.argument_sources)

    @property
    def has_secret(self) -> bool:
        return any("secret" in source.lower() for source in self.argument_sources)


@dataclass(frozen=True)
class ActionContract:
    tool: str
    operation: str
    arguments: dict[str, Any]
    intent: str
    action_id: str = field(default_factory=lambda: f"act_{uuid4().hex[:12]}")
    expected_effects: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()
    permissions_required: tuple[str, ...] = ("workspace:read",)
    provenance: Provenance = field(default_factory=Provenance)
    reversible: bool = True
    rollback_strategy: str | None = None
    preconditions: tuple[str, ...] = ()
    postconditions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ActionContract":
        required = ("tool", "operation", "arguments", "intent")
        missing = [name for name in required if name not in data]
        if missing:
            raise ValueError(f"ActionContract missing required fields: {', '.join(missing)}")
        if not isinstance(data["arguments"], dict):
            raise TypeError("ActionContract.arguments must be a mapping")

        return cls(
            action_id=str(data.get("action_id") or f"act_{uuid4().hex[:12]}"),
            tool=str(data["tool"]),
            operation=str(data["operation"]),
            arguments=dict(data["arguments"]),
            intent=str(data["intent"]),
            expected_effects=tuple(str(x) for x in data.get("expected_effects", ())),
            resources=tuple(str(x) for x in data.get("resources", ())),
            permissions_required=tuple(str(x) for x in data.get("permissions_required", ("workspace:read",))),
            provenance=Provenance.from_mapping(data.get("provenance")),
            reversible=bool(data.get("reversible", True)),
            rollback_strategy=data.get("rollback_strategy"),
            preconditions=tuple(str(x) for x in data.get("preconditions", ())),
            postconditions=tuple(str(x) for x in data.get("postconditions", ())),
            metadata=dict(data.get("metadata", {})),
        )

    @property
    def action_class(self) -> ActionClass:
        return classify_action(self)

    @property
    def mutates_state(self) -> bool:
        return is_state_mutating(self.action_class)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "tool": self.tool,
            "operation": self.operation,
            "arguments": self.arguments,
            "intent": self.intent,
            "expected_effects": list(self.expected_effects),
            "resources": list(self.resources),
            "permissions_required": list(self.permissions_required),
            "provenance": self.provenance.to_dict(),
            "reversible": self.reversible,
            "rollback_strategy": self.rollback_strategy,
            "preconditions": list(self.preconditions),
            "postconditions": list(self.postconditions),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ContractValidation:
    allowed: bool
    reasons: tuple[str, ...] = ()

    @classmethod
    def pass_(cls) -> "ContractValidation":
        return cls(allowed=True)

    @classmethod
    def fail(cls, *reasons: str) -> "ContractValidation":
        return cls(allowed=False, reasons=tuple(reasons))


def validate_schema(contract: ActionContract) -> ContractValidation:
    reasons: list[str] = []
    if not contract.tool.strip():
        reasons.append("tool is empty")
    if not contract.operation.strip():
        reasons.append("operation is empty")
    if not isinstance(contract.arguments, dict):
        reasons.append("arguments is not a mapping")
    if not contract.intent.strip():
        reasons.append("intent is empty")
    if contract.mutates_state and not contract.permissions_required:
        reasons.append("mutating action declares no permissions")
    return ContractValidation.fail(*reasons) if reasons else ContractValidation.pass_()
