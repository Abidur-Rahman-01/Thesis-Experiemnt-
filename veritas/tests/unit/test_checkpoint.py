from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.actions.contracts import ActionContract
from veritas.sandbox.base import LocalWorkspaceSandbox
from veritas.sandbox.checkpoint import hash_directory
from veritas.sandbox.checkpoint import FilesystemCheckpoint


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_restore_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sandbox = LocalWorkspaceSandbox(tmp_path)
            sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "x.txt", "content": "one"}, intent="seed"))
            checkpoint = sandbox.checkpoint()

            sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "x.txt", "content": "two"}, intent="mutate"))
            self.assertNotEqual(hash_directory(tmp_path, ignore_names={".veritas_checkpoints"}), checkpoint.state_hash)

            restored_hash = sandbox.restore(checkpoint)

            self.assertEqual(restored_hash, checkpoint.state_hash)
            self.assertEqual((tmp_path / "x.txt").read_text(encoding="utf-8"), "one")

    def test_restore_rejects_snapshot_outside_checkpoint_store(self) -> None:
        with TemporaryDirectory() as tmp, TemporaryDirectory() as outside:
            sandbox = LocalWorkspaceSandbox(Path(tmp))
            fake = FilesystemCheckpoint("cp_fake", Path(outside), hash_directory(outside))

            with self.assertRaisesRegex(ValueError, "outside"):
                sandbox.restore(fake)

    def test_restore_rejects_tampered_snapshot(self) -> None:
        with TemporaryDirectory() as tmp:
            sandbox = LocalWorkspaceSandbox(Path(tmp))
            sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "x.txt", "content": "one"}, intent="seed"))
            checkpoint = sandbox.checkpoint()
            (checkpoint.snapshot_path / "x.txt").write_text("tampered", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "hash"):
                sandbox.restore(checkpoint)
