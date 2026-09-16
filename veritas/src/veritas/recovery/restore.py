"""Restore helpers."""

from __future__ import annotations

from pathlib import Path

from veritas.core.state import CheckpointRecord
from veritas.sandbox.base import Sandbox
from veritas.sandbox.checkpoint import FilesystemCheckpoint


def restore_checkpoint(sandbox: Sandbox, record: CheckpointRecord) -> str:
    checkpoint = FilesystemCheckpoint(
        checkpoint_id=record.checkpoint_id,
        snapshot_path=Path(record.path),
        state_hash=record.state_hash,
    )
    restored_hash = sandbox.restore(checkpoint)
    if restored_hash != record.state_hash:
        raise RuntimeError(f"restore hash mismatch: expected {record.state_hash}, got {restored_hash}")
    return restored_hash
