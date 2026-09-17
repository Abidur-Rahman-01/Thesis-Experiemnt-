"""Validate a frozen Paper 1 manifest and optionally launch mini-SWE-agent."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from pathlib import Path

from veritas.eval.swebench import build_minisweagent_command, load_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--mini-swe-root", type=Path, default=Path("../mini-swe-agent"))
    parser.add_argument("--output", type=Path, default=Path("research/results/swebench"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    command = build_minisweagent_command(
        manifest,
        mini_swe_root=args.mini_swe_root,
        output_dir=args.output,
        model=args.model,
        workers=args.workers,
    )
    print(shlex.join(command))
    if not args.execute:
        print("dry run only; pass --execute to launch the benchmark")
        return

    env = os.environ.copy()
    mini_src = str((args.mini_swe_root / "src").resolve())
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (mini_src, env.get("PYTHONPATH", ""))))
    subprocess.run(command, env=env, check=True)


if __name__ == "__main__":
    main()
