"""Convert mini-SWE-agent trajectory JSON files to VERITAS JSONL records."""

from __future__ import annotations

import argparse
from pathlib import Path

from veritas.eval.trajectory import import_miniswe_trajectory
from veritas.storage.events import JSONLEventStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trajectory_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--append", action="store_true", help="append to an existing JSONL file")
    args = parser.parse_args()

    paths = sorted(args.trajectory_root.rglob("*.traj.json"))
    if not paths:
        raise SystemExit(f"no *.traj.json files found under {args.trajectory_root}")
    if args.output.exists() and not args.append:
        raise SystemExit(f"output already exists: {args.output}; remove it or pass --append")
    records = [record for path in paths for record in import_miniswe_trajectory(path)]
    store = JSONLEventStore(args.output)
    store.extend(records)
    print(f"imported {len(records)} actions from {len(paths)} trajectories into {args.output}")


if __name__ == "__main__":
    main()
