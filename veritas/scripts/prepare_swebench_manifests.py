"""Create deterministic, non-overlapping Paper 1 SWE-bench manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veritas.eval.swebench import load_swebench_metadata, manifest_payload, partition_tasks


DEFAULT_STAGES = (
    "development=40",
    "label_train=100",
    "calibration=80",
    "validation=80",
    "final_test=160",
    "robustness=40",
)


def parse_stage_sizes(values: list[str]) -> dict[str, int]:
    stages: dict[str, int] = {}
    for value in values:
        try:
            name, raw_size = value.split("=", 1)
            size = int(raw_size)
        except ValueError as exc:
            raise ValueError(f"invalid stage specification {value!r}; expected NAME=COUNT") from exc
        name = name.strip()
        if not name or size < 0:
            raise ValueError(f"invalid stage specification {value!r}")
        if name in stages:
            raise ValueError(f"duplicate stage: {name}")
        stages[name] = size
    return stages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path, help="exported SWE-bench JSON or JSONL metadata")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--source-revision", required=True, help="dataset commit or immutable revision")
    parser.add_argument("--dataset", default="verified")
    parser.add_argument("--split", default="test")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--stage",
        action="append",
        dest="stages",
        metavar="NAME=COUNT",
        help="repeat to override the default 500-task partition",
    )
    parser.add_argument("--force", action="store_true", help="replace existing manifest files")
    args = parser.parse_args()

    stage_sizes = parse_stage_sizes(args.stages or list(DEFAULT_STAGES))
    tasks, source_sha256 = load_swebench_metadata(args.metadata)
    partitions = partition_tasks(tasks, stage_sizes, seed=args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for stage, stage_tasks in partitions.items():
        output = args.output_dir / f"paper1_{stage}.json"
        if output.exists() and not args.force:
            raise SystemExit(f"manifest already exists: {output}; pass --force to replace it")
        payload = manifest_payload(
            stage_tasks,
            stage=stage,
            dataset=args.dataset,
            split=args.split,
            source_revision=args.source_revision,
            source_sha256=source_sha256,
            seed=args.seed,
        )
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(output)

    summary = {
        "source_sha256": source_sha256,
        "selection_seed": args.seed,
        "available_tasks": len(tasks),
        "selected_tasks": sum(stage_sizes.values()),
        "stages": stage_sizes,
        "manifests": [str(path) for path in written],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
