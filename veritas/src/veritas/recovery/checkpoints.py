"""Recovery checkpoint helpers."""

from __future__ import annotations

from dataclasses import dataclass

from veritas.core.state import CheckpointRecord
from veritas.sandbox.base import Sandbox


@dataclass
class CheckpointManager:
    sandbox: Sandbox

    def create(self, step: int) -> CheckpointRecord:
        checkpoint = self.sandbox.checkpoint()
        return CheckpointRecord(
            checkpoint_id=checkpoint.checkpoint_id,
            step=step,
            state_hash=checkpoint.state_hash,
            path=str(checkpoint.snapshot_path),
        )
