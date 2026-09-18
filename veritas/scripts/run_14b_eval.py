"""14B Parameter Model Scaling & Comparative Evaluation for VERITAS.

Benchmarks qwen2.5-coder:14b against 7B and 3B architectures on:
1. Mathematical & Symbolic Reasoning Accuracy (GSM8K)
2. Typed Action Contract Formulation (Zero-shot JSON)
3. Error Probability Estimation & Calibration
4. GPU Inference Latency & Token Throughput on NVIDIA GeForce RTX 5080
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from veritas.eval.gsm8k import load_gsm8k_dataset
from veritas.models.base import PolicyContext
from veritas.models.ollama_client import OllamaClient, OllamaErrorEstimator, OllamaPolicy


def run_comprehensive_eval(models: list[str], problems_count: int = 5) -> list[dict]:
    results = []
    problems = load_gsm8k_dataset(limit=problems_count)

    for model_name in models:
        client = OllamaClient(model_name=model_name)
        if not client.is_available():
            results.append({"model": model_name, "status": "failed", "error": "Ollama server offline"})
            continue

        installed = client.list_models()
        matching = [m for m in installed if model_name in m]
        if not matching:
            results.append({"model": model_name, "status": "not_installed", "error": f"Model '{model_name}' not in Ollama"})
            continue

        full_name = matching[0]
        client.model_name = full_name
        policy = OllamaPolicy(client)
        estimator = OllamaErrorEstimator(client)

        print(f"\n=======================================================")
        print(f"--> EVALUATING OPEN-SOURCE MODEL: {full_name}")
        print(f"=======================================================")

        # 1. Multi-Step Reasoning
        correct = 0
        gen_latencies = []
        for prob in problems:
            prompt = (
                f"Solve this multi-step problem step by step.\n"
                f"Question: {prob.question}\n"
                f"Conclude with exactly '#### <number>' on the last line."
            )
            t0 = time.perf_counter()
            resp = client.generate(prompt, temperature=0.0)
            t1 = time.perf_counter()
            gen_latencies.append((t1 - t0) * 1000.0)

            # Verification of final answer
            target_str = str(int(prob.final_answer)) if prob.final_answer.is_integer() else str(prob.final_answer)
            if f"#### {target_str}" in resp or f"####  {target_str}" in resp:
                correct += 1

        avg_gen_latency = sum(gen_latencies) / max(1, len(gen_latencies))
        accuracy = (correct / max(1, len(problems))) * 100.0

        # 2. Action Contract Structuring
        ctx = PolicyContext(
            goal="Scan application logs for CVE-2024 unauthorized access attempts and quarantine tainted sessions",
            step_index=0,
            history=(),
        )
        t0 = time.perf_counter()
        action = policy.propose_action(ctx)
        t1 = time.perf_counter()
        contract_latency = (t1 - t0) * 1000.0
        has_valid_contract = action is not None and bool(action.tool) and bool(action.operation)

        # 3. Error Probability & Risk Estimation
        if action:
            t0 = time.perf_counter()
            est = estimator.estimate(ctx, action)
            t1 = time.perf_counter()
            est_latency = (t1 - t0) * 1000.0
            est_score = est.raw_score
        else:
            est_latency = 0.0
            est_score = 0.0

        res_dict = {
            "model": full_name,
            "parameter_scale": "14B" if "14b" in full_name else ("7B" if "7b" in full_name else "3B"),
            "problems_evaluated": len(problems),
            "reasoning_accuracy_percent": round(accuracy, 1),
            "avg_generation_latency_ms": round(avg_gen_latency, 1),
            "contract_structuring_latency_ms": round(contract_latency, 1),
            "valid_contract_produced": has_valid_contract,
            "chosen_tool": action.tool if action else "none",
            "chosen_operation": action.operation if action else "none",
            "action_intent": action.intent if action else "none",
            "error_risk_score": round(est_score, 2),
            "risk_estimation_latency_ms": round(est_latency, 1),
        }
        results.append(res_dict)
        print(f"Result for {full_name}: Accuracy={accuracy:.1f}%, GenLatency={avg_gen_latency:.1f}ms, Contract={has_valid_contract}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate 14B scaling against 7B and 3B models")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama3.2:3b", "qwen2.5-coder:7b", "qwen2.5-coder:14b"],
        help="Model list to evaluate",
    )
    parser.add_argument("--problems", type=int, default=5, help="Number of test reasoning problems")
    parser.add_argument("--output", type=Path, default=Path("research/results/scaling_14b_eval.json"))
    args = parser.parse_args()

    results = run_comprehensive_eval(args.models, problems_count=args.problems)

    print("\n" + "=" * 104)
    print("VERITAS PARAMETER SCALING BENCHMARK (3B vs 7B vs 14B on NVIDIA GeForce RTX 5080)")
    print("=" * 104)
    header = (
        f"{'Model Name':<20} | {'Scale':<6} | {'Accuracy':<9} | {'Gen Latency':<13} | "
        f"{'Structuring':<13} | {'Valid Contract'}"
    )
    print(header)
    print("-" * 104)
    for r in results:
        if r.get("status") in ("failed", "not_installed"):
            print(f"{r['model']:<20} | {'--':<6} | ERROR: {r['error']}")
            continue
        row = (
            f"{r['model']:<20} | {r['parameter_scale']:<6} | {r['reasoning_accuracy_percent']:>6.1f}%   | "
            f"{r['avg_generation_latency_ms']:>8.1f} ms   | {r['contract_structuring_latency_ms']:>8.1f} ms   | "
            f"{'YES (' + r['chosen_tool'] + ')' if r['valid_contract_produced'] else 'NO'}"
        )
        print(row)
    print("=" * 104)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    csv_path = args.output.with_suffix(".csv")
    csv_lines = [
        "model,parameter_scale,accuracy_percent,gen_latency_ms,structuring_latency_ms,valid_contract,chosen_tool,error_risk_score"
    ]
    for r in results:
        if r.get("status") not in ("failed", "not_installed"):
            csv_lines.append(
                f"{r['model']},{r['parameter_scale']},{r['reasoning_accuracy_percent']},{r['avg_generation_latency_ms']},"
                f"{r['contract_structuring_latency_ms']},{r['valid_contract_produced']},{r['chosen_tool']},{r['error_risk_score']}"
            )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    print(f"Results saved to: {args.output} and {csv_path}\n")


if __name__ == "__main__":
    main()
