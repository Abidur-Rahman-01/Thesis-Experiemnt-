import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.eval.swebench import build_minisweagent_command, load_manifest


class SwebenchManifestTests(unittest.TestCase):
    def test_frozen_manifest_builds_exact_task_filter(self) -> None:
        payload = {
            "dataset": "verified",
            "split": "test",
            "frozen": True,
            "source_revision": "abc123",
            "tasks": [{"task_id": "owner__repo-1", "repository": "owner/repo"}],
        }
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            manifest = load_manifest(path)
            command = build_minisweagent_command(
                manifest, mini_swe_root="../mini-swe-agent", output_dir="out", model="test/model"
            )

        self.assertIn("^(?:owner__repo\\-1)$", command)
        self.assertIn("test/model", command)

    def test_unfrozen_manifest_is_rejected(self) -> None:
        payload = {
            "dataset": "verified",
            "split": "test",
            "frozen": False,
            "tasks": [{"task_id": "owner__repo-1", "repository": "owner/repo"}],
        }
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            manifest = load_manifest(path)
            with self.assertRaisesRegex(ValueError, "not frozen"):
                build_minisweagent_command(
                    manifest, mini_swe_root="../mini-swe-agent", output_dir="out", model="test/model"
                )
