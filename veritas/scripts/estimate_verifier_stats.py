"""Estimate class-level verifier detection and false-positive rates."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from veritas.storage.events import JSONLEventStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    args = parser.parse_args()

    buckets: dict[str, list[dict]] = defaultdict(list)
    for record in JSONLEventStore(args.records).read_all():
        if record.get("ground_truth_label") in {"error", "correct"} and record.get("verifier_verdict"):
            buckets[str(record.get("action_class", "unknown"))].append(record)

    output = {}
    for action_class, records in buckets.items():
        errors = [r for r in records if r["ground_truth_label"] == "error"]
        correct = [r for r in records if r["ground_truth_label"] == "correct"]
        detection = sum(1 for r in errors if r.get("verifier_verdict") == "fail") / len(errors) if errors else 0.5
        false_positive = sum(1 for r in correct if r.get("verifier_verdict") == "fail") / len(correct) if correct else 0.1
        output[action_class] = {
            "detection_rate": detection,
            "false_positive_rate": false_positive,
            "error_count": len(errors),
            "correct_count": len(correct),
        }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
