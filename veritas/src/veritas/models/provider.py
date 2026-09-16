"""Provider-facing policy adapters.

The production/provider implementation is intentionally not included here. For
local tests and development, `ScriptedPolicy` provides deterministic contracts.
"""

from __future__ import annotations

from dataclasses import dataclass

from veritas.actions.contracts import ActionContract
from veritas.models.base import PolicyContext


@dataclass
class ScriptedPolicy:
    actions: list[ActionContract]

    def propose_action(self, context: PolicyContext) -> ActionContract | None:
        if context.step_index >= len(self.actions):
            return None
        return self.actions[context.step_index]
