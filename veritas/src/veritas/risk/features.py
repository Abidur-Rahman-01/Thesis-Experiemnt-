"""Transparent action-impact features."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.classes import ActionClass
from veritas.actions.contracts import ActionContract


@dataclass(frozen=True)
class ImpactFeatures:
    mutation: float = 0.0
    irreversible: float = 0.0
    privilege: float = 0.0
    external: float = 0.0
    secret: float = 0.0
    untrusted: float = 0.0
    scope: float = 0.0

    @classmethod
    def from_contract(cls, contract: ActionContract) -> "ImpactFeatures":
        action_class = contract.action_class
        permissions = " ".join(contract.permissions_required).lower()
        resources = list(contract.resources)

        privileged = any(prefix in permissions for prefix in ("admin:", "secret:", "network:", "external:"))
        external = action_class is ActionClass.EXTERNAL_MUTATION or "network:" in permissions or "external:" in permissions
        secret = contract.provenance.has_secret or "secret:" in permissions
        scope = min(1.0, len(resources) / 10.0)

        return cls(
            mutation=1.0 if contract.mutates_state else 0.0,
            irreversible=0.0 if contract.reversible else 1.0,
            privilege=1.0 if privileged else 0.0,
            external=1.0 if external else 0.0,
            secret=1.0 if secret else 0.0,
            untrusted=1.0 if contract.provenance.has_untrusted else 0.0,
            scope=scope,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "mutation": self.mutation,
            "irreversible": self.irreversible,
            "privilege": self.privilege,
            "external": self.external,
            "secret": self.secret,
            "untrusted": self.untrusted,
            "scope": self.scope,
        }
