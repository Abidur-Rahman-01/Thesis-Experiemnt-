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

Export the SWE-bench Verified metadata as JSONL, then create deterministic non-overlapping manifests. The default partition is development 40, label/train 100, calibration 80, validation 80, final test 160, and robustness 40.

```powershell
py -m pip install datasets
$env:PYTHONPATH = "src"
py scripts\export_swebench_metadata.py `
  research\swebench_verified.jsonl `
  --revision DATASET_COMMIT_OR_IMMUTABLE_REVISION
```

Use an immutable dataset revision for a final experiment. Omitting `--revision` is acceptable only while testing the infrastructure.

```powershell
$env:PYTHONPATH = "src"
py scripts\prepare_swebench_manifests.py `
  path\to\swebench_verified.jsonl `
  configs\benchmarks `
  --source-revision DATASET_COMMIT_OR_REVISION
```

The generated manifests are frozen and record the selection seed plus the SHA-256 of the source metadata. Use `--stage development=20 --stage calibration=10` for a small infrastructure smoke test; do not treat that small split as a final experimental design.

Validate and preview the exact mini-SWE-agent command without downloading or spending model credits:

```bash
PYTHONPATH=src python3 scripts/run_swebench.py \
  --manifest configs/benchmarks/paper1_development.json \
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
