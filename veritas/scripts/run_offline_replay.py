"""Run offline replay from JSONL records or the built-in demo dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_baseline import demo_records
from veritas.eval.baselines import default_schedulers
from veritas.eval.replay import ReplayEngine
from veritas.storage.events import JSONLEventStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, help="JSONL event/action log")
    parser.add_argument("--budget", type=float, action="append")
    parser.add_argument("--output", type=Path, help="write results to JSON file")
    args = parser.parse_args()

    records = JSONLEventStore(args.events).read_all() if args.events else list(demo_records())
    budgets = args.budget if args.budget is not None else [0.03, 0.06, 0.12]
    results = ReplayEngine(tuple(records)).sweep(default_schedulers(), budgets)
    payload = json.dumps([result.to_dict() for result in results], indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"saved replay results to {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
