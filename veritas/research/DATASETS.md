# VERITAS Paper 1 Data Requirements

VERITAS does not require a private external dataset to begin. The primary external benchmark is the public **SWE-bench Verified** split exposed by the Hugging Face dataset `princeton-nlp/SWE-Bench_Verified`. mini-SWE-agent downloads the task metadata and the corresponding SWE-bench Docker images when a run is executed.

## Required external artifacts

1. **SWE-bench Verified task metadata and evaluation images**
   - Dataset: `princeton-nlp/SWE-Bench_Verified`
   - Intended size: 500 human-validated tasks
   - Use: development subset, trajectory collection subset, pilot, and final online evaluation
   - Acquisition: handled by mini-SWE-agent and Docker when `scripts/run_swebench.py --execute` is used

2. **Model weights or provider access**
   - Policy: choose and pin one capable coding model before trajectory collection
   - Verifier: the blueprint proposes `Qwen/Qwen2.5-Coder-7B-Instruct` as a local reference candidate
   - Record the exact model revision, quantization, serving stack, and prompt hash

3. **Human/adjudicated action labels**
   - This dataset must be produced by the project; it is not an off-the-shelf download
   - Preserve deterministic test evidence separately from human semantic judgments
   - Never derive semantic ground truth from execution success or the same verifier score being evaluated

4. **Controlled recovery trials**
   - Generate from frozen SWE-bench development tasks using seeded fault injection
   - Store the fault type, seed, checkpoint, recovery strategy, repeated cost, final outcome, and residual damage

## Optional future dataset

AgentDojo is already vendored at `../agentdojo`. It is reserved for the post-Paper-1 security track measuring indirect prompt-injection attack success and benign utility. It is not part of the primary RC-VoV claim.

## Manifest workflow

Copy `configs/benchmarks/paper1_tasks.example.json` to a stage-specific JSON manifest. Replace the placeholder task, record the dataset revision, choose the task IDs before viewing final method performance, and set `frozen` to `true` only after review.

Validate and preview the exact mini-SWE-agent command without downloading or spending model credits:

```bash
PYTHONPATH=src python3 scripts/run_swebench.py \
  --manifest configs/benchmarks/paper1_dev.json \
  --model PROVIDER/MODEL
```

Add `--execute` only when Docker, model credentials or local inference, and the frozen task list are ready.

After a run, convert trajectories to the VERITAS action schema:

```bash
PYTHONPATH=src python3 scripts/import_miniswe_trajectories.py \
  research/results/swebench \
  research/results/actions.raw.jsonl
```

Imported records deliberately retain `unresolved` labels and null risk fields. Calibration, impact scoring, verification, and adjudication must be performed as separate, auditable stages.
