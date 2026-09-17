import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.eval.trajectory import import_miniswe_trajectory


class MiniSweTrajectoryTests(unittest.TestCase):
    def test_imports_action_observation_and_outcome(self) -> None:
        payload = {
            "instance_id": "owner__repo-1",
            "trajectory_format": "mini-swe-agent-1.1",
            "info": {"exit_status": "submitted"},
            "messages": [
                {
                    "role": "assistant",
                    "content": "inspect",
                    "extra": {
                        "actions": [{"command": "pytest -q"}],
                        "cost": 0.01,
                        "usage": {"prompt_tokens": 10, "completion_tokens": 4},
                    },
                },
                {
                    "role": "tool",
                    "content": "ok",
                    "extra": {"raw_output": "1 passed", "returncode": 0},
                },
            ],
        }
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.traj.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            records = import_miniswe_trajectory(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["task_id"], "owner__repo-1")
        self.assertEqual(records[0]["action_class"], "test")
        self.assertEqual(records[0]["input_tokens"], 10)
        self.assertTrue(records[0]["execution_success"])
        self.assertEqual(records[0]["ground_truth_label"], "unresolved")

    def test_imports_legacy_fenced_command(self) -> None:
        payload = [
            {"role": "assistant", "content": "```mswea_bash_command\nrg TODO src\n```"},
            {"role": "user", "content": "<returncode>1</returncode>\n<output>not found</output>"},
        ]
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.traj.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            records = import_miniswe_trajectory(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["action_class"], "search")
        self.assertFalse(records[0]["execution_success"])
        self.assertEqual(records[0]["observation"], "not found")
        self.assertEqual(records[0]["action_json"]["permissions_required"], ["workspace:read"])
