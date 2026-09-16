import unittest

from scripts.label_actions import label_record


class LabelActionTests(unittest.TestCase):
    def test_execution_success_is_not_semantic_ground_truth(self) -> None:
        record = label_record({"execution_success": True, "verifier_verdict": "pass"})

        self.assertEqual(record["ground_truth_label"], "unresolved")
        self.assertEqual(record["label_source"], "unlabeled")

    def test_existing_adjudicated_label_is_preserved(self) -> None:
        record = label_record({"ground_truth_label": "error", "label_source": "human_adjudication"})

        self.assertEqual(record["ground_truth_label"], "error")
        self.assertEqual(record["label_source"], "human_adjudication")


if __name__ == "__main__":
    unittest.main()
