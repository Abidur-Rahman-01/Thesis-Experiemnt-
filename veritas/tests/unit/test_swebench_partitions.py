import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from veritas.eval.swebench import load_swebench_metadata, manifest_payload, partition_tasks


class SwebenchPartitionTests(unittest.TestCase):
    def test_partitions_are_reproducible_and_disjoint(self) -> None:
        rows = [
            {"instance_id": f"owner__repo-{index}", "repo": "owner/repo", "base_commit": str(index)}
            for index in range(10)
        ]
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "tasks.json"
            source.write_text(json.dumps(rows), encoding="utf-8")
            tasks, source_hash = load_swebench_metadata(source)

        first = partition_tasks(tasks, {"development": 4, "calibration": 3, "final_test": 3}, seed=42)
        second = partition_tasks(list(reversed(tasks)), {"development": 4, "calibration": 3, "final_test": 3}, seed=42)
        self.assertEqual(first, second)
        all_ids = [task.task_id for group in first.values() for task in group]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(len(source_hash), 64)

    def test_manifest_records_freeze_metadata(self) -> None:
        rows = [{"instance_id": "owner__repo-1", "repo": "owner/repo"}]
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "tasks.jsonl"
            source.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
            tasks, source_hash = load_swebench_metadata(source)
        payload = manifest_payload(
            tuple(tasks),
            stage="development",
            dataset="verified",
            split="test",
            source_revision="abc123",
            source_sha256=source_hash,
            seed=7,
        )
        self.assertTrue(payload["frozen"])
        self.assertEqual(payload["selection_seed"], 7)
        self.assertEqual(payload["source_sha256"], source_hash)

    def test_rejects_oversized_partition(self) -> None:
        with self.assertRaisesRegex(ValueError, "requested 2 tasks"):
            partition_tasks([], {"development": 2}, seed=42)
