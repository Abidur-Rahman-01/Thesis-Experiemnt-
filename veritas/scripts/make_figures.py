"""Convert replay JSON to simple CSV-like rows for plotting elsewhere."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay_json", type=Path)
    parser.add_argument("--output", "-o", type=Path, help="CSV output file path")
    args = parser.parse_args()

    raw = args.replay_json.read_bytes()
    rows = None
    for enc in ("utf-8-sig", "utf-8", "utf-16", "latin1"):
        try:
            rows = json.loads(raw.decode(enc))
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    if rows is None:
        raise SystemExit(f"could not parse valid JSON from {args.replay_json}")

    lines = ["policy,budget,verification_cost,consequential_errors_caught,errors_caught,false_rejections"]
    for row in rows:
        lines.append(
            f"{row['policy_name']},{row['budget']},{row['verification_cost']},"
            f"{row['consequential_errors_caught']},{row['errors_caught']},{row['false_rejections']}"
        )
    csv_content = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(csv_content, encoding="utf-8")
        print(f"saved CSV figures data to {args.output}")
    else:
        print(csv_content.strip())


if __name__ == "__main__":
    main()
