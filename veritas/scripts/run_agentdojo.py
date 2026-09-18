"""Run AgentDojo security evaluation: Base Agent vs VERITAS Sentinel Defense."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veritas.eval.agentdojo_bench import AgentDojoTask, evaluate_baseline, evaluate_veritas, load_agentdojo_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate VERITAS on AgentDojo Security Benchmark")
    parser.add_argument("--dataset-path", type=Path, default=None, help="Path to custom AgentDojo JSON file")
    parser.add_argument("--domain", type=str, default=None, choices=["workspace", "slack", "banking", "travel"], help="Filter domain")
    parser.add_argument("--output", type=Path, default=Path("research/results/agentdojo_eval.json"))
    args = parser.parse_args()

    tasks = load_agentdojo_suite(args.dataset_path, domain=args.domain)
    domain_label = args.domain.upper() if args.domain else "ALL DOMAINS (Workspace, Slack, Banking, Travel)"
    print(f"Loaded {len(tasks)} AgentDojo security benchmark tasks [{domain_label}]")

    base_results = evaluate_baseline(tasks)
    veritas_results = evaluate_veritas(tasks)
    combined = [base_results, veritas_results]

    # Print summary table
    print("\n" + "=" * 98)
    print(f"TRACK 3: AGENTDOJO TOOL SECURITY & PROMPT INJECTION BENCHMARK ({domain_label})")
    print("=" * 98)
    header = f"{'System Architecture':<28} | {'Total':<6} | {'Adv Tasks':<10} | {'ASR (Attack %)' :<16} | {'Defended %':<12} | {'Benign Utility'}"
    print(header)
    print("-" * 98)
    for r in combined:
        row = (
            f"{r['model']:<28} | {r['tasks_total']:<6} | {r['adversarial_tasks']:<10} | "
            f"{r['attack_success_rate_asr']:>5.1f}%          | {r['defended_rate']:>5.1f}%      | {r['benign_utility_rate']:>5.1f}%"
        )
        print(row)
    print("=" * 98)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    csv_path = args.output.with_suffix(".csv")
    csv_lines = [
        "architecture,tasks_total,adversarial_tasks,attacks_succeeded,asr_percent,defended_percent,benign_tasks,benign_utility_percent"
    ]
    for r in combined:
        csv_lines.append(
            f"{r['model']},{r['tasks_total']},{r['adversarial_tasks']},{r['attacks_succeeded']},"
            f"{r['attack_success_rate_asr']},{r['defended_rate']},{r['benign_tasks']},{r['benign_utility_rate']}"
        )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    print(f"Detailed benchmark metrics saved to: {args.output}")
    print(f"Benchmark summary CSV saved to: {csv_path}\n")


if __name__ == "__main__":
    main()
