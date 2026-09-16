from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.__main__ import build_demo_runtime


class RuntimeIntegrationTests(unittest.TestCase):
    def test_demo_runtime_executes_and_logs_event(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runtime = build_demo_runtime(tmp_path)

            state = runtime.run("write answer")

            self.assertEqual(state.termination_status, "completed")
            self.assertEqual(len(state.actions), 1)
            self.assertTrue(state.actions[0].executed)
            self.assertEqual(state.actions[0].ground_truth_label, "unresolved")
            self.assertEqual((tmp_path / "answer.txt").read_text(encoding="utf-8"), "verified\n")
