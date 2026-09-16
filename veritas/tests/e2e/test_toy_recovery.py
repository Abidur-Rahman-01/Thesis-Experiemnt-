from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.actions.contracts import ActionContract
from veritas.core.state import CheckpointRecord
from veritas.recovery.restore import restore_checkpoint
from veritas.sandbox.base import LocalWorkspaceSandbox


class ToyRecoveryTests(unittest.TestCase):
    def test_restore_checkpoint_helper_validates_hash(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sandbox = LocalWorkspaceSandbox(tmp_path)
            sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "a.txt", "content": "good"}, intent="seed"))
            cp = sandbox.checkpoint()
            record = CheckpointRecord(cp.checkpoint_id, step=0, state_hash=cp.state_hash, path=str(cp.snapshot_path))

            sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "a.txt", "content": "bad"}, intent="fault"))
            restored = restore_checkpoint(sandbox, record)

            self.assertEqual(restored, cp.state_hash)
            self.assertEqual((tmp_path / "a.txt").read_text(encoding="utf-8"), "good")
