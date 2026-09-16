"""Collect a toy VERITAS trajectory into a JSONL event log."""

from __future__ import annotations

import argparse
from pathlib import Path

from veritas.__main__ import build_demo_runtime
from veritas.storage.events import JSONLEventStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path("research/results/toy_workspace"))
    parser.add_argument("--events", type=Path, default=Path("research/results/events.jsonl"))
    args = parser.parse_args()

    runtime = build_demo_runtime(args.workspace)
    runtime.event_store = JSONLEventStore(args.events)
    state = runtime.run("collect a toy trajectory")
    print(f"run_id={state.run_id} status={state.termination_status} events={len(state.actions)}")


if __name__ == "__main__":
    main()
