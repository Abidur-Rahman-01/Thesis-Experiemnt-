"""Fit a temperature calibrator from JSONL action records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veritas.eval.metrics import calibration_report
from veritas.risk.calibrator import TemperatureCalibrator
from veritas.storage.events import JSONLEventStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    args = parser.parse_args()

    records = [r for r in JSONLEventStore(args.records).read_all() if r.get("ground_truth_label") in {"error", "correct"}]
    raw = [float(r["raw_error_score"]) for r in records]
    labels = [1 if r["ground_truth_label"] == "error" else 0 for r in records]
    calibrator = TemperatureCalibrator.fit(raw, labels) if records else TemperatureCalibrator()
    probs = calibrator.calibrate_many(raw)
    report = calibration_report(probs, labels) if records else {}
    print(json.dumps({"temperature": calibrator.temperature, "examples": len(records), "report": report}, indent=2))


if __name__ == "__main__":
    main()
