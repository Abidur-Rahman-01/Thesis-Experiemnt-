"""Filesystem checkpointing for local research sandboxes."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


def hash_directory(path: str | Path, *, ignore_names: set[str] | None = None) -> str:
    root = Path(path)
    ignore = ignore_names or set()
    digest = hashlib.sha256()
    for file_path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = file_path.relative_to(root)
        if any(part in ignore for part in rel.parts):
            continue
        digest.update(str(rel).encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


@dataclass(frozen=True)
class FilesystemCheckpoint:
    checkpoint_id: str
    snapshot_path: Path
    state_hash: str


@dataclass
class DirectoryCheckpointStore:
    workspace: Path
    checkpoint_root: Path | None = None

    def __post_init__(self) -> None:
        self.workspace = Path(self.workspace)
        if self.checkpoint_root is None:
            self.checkpoint_root = self.workspace / ".veritas_checkpoints"
        self.checkpoint_root.mkdir(parents=True, exist_ok=True)

    def checkpoint(self) -> FilesystemCheckpoint:
        checkpoint_id = f"cp_{uuid4().hex[:12]}"
        snapshot_path = self.checkpoint_root / checkpoint_id
        ignore = {self.checkpoint_root.name}
        shutil.copytree(self.workspace, snapshot_path, ignore=shutil.ignore_patterns(*ignore))
        state_hash = hash_directory(self.workspace, ignore_names=ignore)
        return FilesystemCheckpoint(checkpoint_id=checkpoint_id, snapshot_path=snapshot_path, state_hash=state_hash)

    def restore(self, checkpoint: FilesystemCheckpoint) -> str:
        checkpoint_root = self.checkpoint_root.resolve()
        snapshot_path = checkpoint.snapshot_path.resolve()
        if checkpoint_root not in snapshot_path.parents or not snapshot_path.is_dir():
            raise ValueError("checkpoint snapshot is outside the checkpoint store")
        snapshot_hash = hash_directory(snapshot_path)
        if snapshot_hash != checkpoint.state_hash:
            raise ValueError("checkpoint snapshot hash does not match its recorded state")

        ignore_name = self.checkpoint_root.name
        for child in self.workspace.iterdir():
            if child.name == ignore_name:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

        for child in snapshot_path.iterdir():
            target = self.workspace / child.name
            if child.is_dir():
                shutil.copytree(child, target)
            else:
                shutil.copy2(child, target)
        return hash_directory(self.workspace, ignore_names={ignore_name})
