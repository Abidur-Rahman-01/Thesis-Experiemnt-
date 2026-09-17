"""Export the public SWE-bench Verified metadata used to freeze task splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--dataset", default="princeton-nlp/SWE-Bench_Verified")
    parser.add_argument("--split", default="test")
    parser.add_argument("--revision", help="immutable Hugging Face dataset revision")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.force:
        raise SystemExit(f"output already exists: {args.output}; pass --force to replace it")
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("missing dependency: install it with 'py -m pip install datasets'") from exc

    kwargs = {"path": args.dataset, "split": args.split}
    if args.revision:
        kwargs["revision"] = args.revision
    dataset = load_dataset(**kwargs)
    fields = ("instance_id", "repo", "base_commit", "problem_statement")
    rows = [{field: row.get(field) for field in fields} for row in dataset]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"exported {len(rows)} tasks to {args.output}")


if __name__ == "__main__":
    main()
