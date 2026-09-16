"""Convert replay JSON to simple CSV-like rows for plotting elsewhere."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay_json", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.replay_json.read_text(encoding="utf-8"))
    print("policy,budget,verification_cost,consequential_errors_caught,errors_caught,false_rejections")
    for row in rows:
        print(
            f"{row['policy_name']},{row['budget']},{row['verification_cost']},"
            f"{row['consequential_errors_caught']},{row['errors_caught']},{row['false_rejections']}"
        )


if __name__ == "__main__":
    main()
