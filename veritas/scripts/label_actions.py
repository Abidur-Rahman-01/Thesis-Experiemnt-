"""Apply simple deterministic labels to action records.

This is a development helper. Publication labels should follow the manifest's
documented evidence hierarchy and keep human/adjudicated labels separate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veritas.storage.events import JSONLEventStore


def label_record(record: dict) -> dict:
    record = dict(record)
    # Execution and verifier outcomes are evidence, not semantic ground truth.
    # Human or task-specific deterministic adjudication must set the label.
    record.setdefault("ground_truth_label", "unresolved")
    record.setdefault("label_source", "unlabeled")
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    records = [label_record(record) for record in JSONLEventStore(args.events).read_all()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"wrote {len(records)} labeled records to {args.output}")


if __name__ == "__main__":
    main()
