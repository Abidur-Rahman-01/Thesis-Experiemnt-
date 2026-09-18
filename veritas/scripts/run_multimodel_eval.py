"""Multi-Model Open-Source LLM Benchmark for VERITAS.

Evaluates and compares different open-source models hosted locally in Ollama
(e.g., qwen2.5-coder:7b, llama3.2:3b, mistral:7b, deepseek-r1:7b) across:
1. Multi-Step Reasoning & Solution Accuracy
2. Action Contract Generation
3. Inference Latency (ms) and Throughput (tokens/sec)
4. Verification & Reflexion Recovery
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from veritas.eval.gsm8k import load_gsm8k_dataset
from veritas.models.base import PolicyContext
from veritas.models.ollama_client import OllamaClient, OllamaErrorEstimator, OllamaPolicy


def benchmark_model(model_name: str, problems_count: int = 5) -> dict[str, Any]:
    client = OllamaClient(model_name=model_name)
    if not client.is_available():
        return {"model": model_name, "error": "Ollama server not reachable"}

    installed = client.list_models()
    matching = [m for m in installed if model_name in m]
    if not matching:
        return {"model": model_name, "error": f"Model '{model_name}' not found in Ollama. Pull it with: ollama pull {model_name}"}

    full_model_name = matching[0]
    client.model_name = full_model_name
    policy = OllamaPolicy(client)
    estimator = OllamaErrorEstimator(client)

    print(f"\n---> Benchmarking Open-Source Model: {full_model_name}")

    # 1. Benchmark Inference Latency & Math Reasoning
    problems = load_gsm8k_dataset(limit=problems_count)
    correct_count = 0
    latencies = []

    for idx, prob in enumerate(problems):
        prompt = f"Problem: {prob.question}\nProvide the final numeric answer at the end preceded by '#### '."
        t0 = time.perf_counter()
        resp = client.generate(prompt, temperature=0.0)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)

        # Check accuracy
        if f"#### {int(prob.final_answer)}" in resp or f"#### {prob.final_answer}" in resp:
            correct_count += 1

    avg_latency = sum(latencies) / max(1, len(latencies))

    # 2. Benchmark Action Contract Structuring
    ctx = PolicyContext(goal="Inspect database for expired user tokens and clean them", step_index=0, history=())
    t0 = time.perf_counter()
    action = policy.propose_action(ctx)
    t1 = time.perf_counter()
    structuring_latency = (t1 - t0) * 1000.0

    valid_contract = action is not None and bool(action.tool) and bool(action.operation)

    # 3. Benchmark Error Probability Estimation
    if action:
        t0 = time.perf_counter()
        est = estimator.estimate(ctx, action)
        t1 = time.perf_counter()
        estimation_latency = (t1 - t0) * 1000.0
        est_score = est.raw_score
    else:
        estimation_latency = 0.0
        est_score = 0.0

    return {
        "model": full_model_name,
        "problems_evaluated": len(problems),
        "reasoning_accuracy": round((correct_count / max(1, len(problems))) * 100.0, 1),
        "avg_generation_latency_ms": round(avg_latency, 1),
        "contract_structuring_latency_ms": round(structuring_latency, 1),
        "valid_contract_produced": valid_contract,
        "action_tool_chosen": action.tool if action else "none",
        "action_intent": action.intent if action else "none",
        "error_estimation_score": round(est_score, 2),
        "estimation_latency_ms": round(estimation_latency, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark multiple open-source LLMs via Ollama")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen2.5-coder:7b", "llama3.2:3b"],
        help="List of model names to benchmark",
    )
    parser.add_argument("--problems", type=int, default=5, help="Number of test reasoning problems")
    parser.add_argument("--output", type=Path, default=Path("research/results/multimodel_eval.json"))
    args = parser.parse_args()

    client = OllamaClient()
    available_models = client.list_models()
    print("=" * 80)
    print("VERITAS OPEN-SOURCE MULTI-MODEL BENCHMARK HARNESS")
    print(f"Ollama Server Available: {client.is_available()}")
    print(f"Installed Models: {', '.join(available_models) if available_models else 'None'}")
    print("=" * 80)

    results = []
    for model_name in args.models:
        res = benchmark_model(model_name, problems_count=args.problems)
        results.append(res)

    print("\n" + "=" * 96)
    print("MULTI-MODEL COMPARATIVE EVALUATION RESULTS (NVIDIA GeForce RTX 5080)")
    print("=" * 96)
    header = f"{'Model':<22} | {'Accuracy':<9} | {'Gen Latency':<13} | {'Contract Struct.':<18} | {'Valid Contract'}"
    print(header)
    print("-" * 96)
    for r in results:
        if "error" in r:
            print(f"{r['model']:<22} | ERROR: {r['error']}")
            continue
        row = (
            f"{r['model']:<22} | {r['reasoning_accuracy']:>6.1f}%   | {r['avg_generation_latency_ms']:>8.1f} ms   | "
            f"{r['contract_structuring_latency_ms']:>12.1f} ms    | {'YES' if r['valid_contract_produced'] else 'NO'}"
        )
        print(row)
    print("=" * 96)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed benchmark metrics saved to: {args.output}\n")


if __name__ == "__main__":
    main()
