# VERITAS

VERITAS is a Paper 1 research runtime for testing whether risk-calibrated value-of-verification (RC-VoV) allocates verification budget better than simpler gates such as calibrated error probability x action impact.

This implementation follows `../VERITAS_updated_research_blueprint.md` rather than the workspace README. It keeps the first research boundary narrow:

- typed `ActionContract` records before execution;
- deterministic permission/schema checks;
- transparent action impact features;
- calibrated action-error probabilities;
- class-level verifier and recovery statistics;
- RC-VoV plus the mandatory baselines;
- checkpointable local sandbox execution for research/toy runs;
- JSONL action/event logging;
- offline matched-budget replay.

Future-only product, security, and training work lives under `future/` and is intentionally not on the Paper 1 critical path.

## Quick Start

Install the package once so commands work consistently on Windows and Linux:

```bash
cd veritas
python -m pip install -e .
python -m unittest discover -s tests
python -m veritas --demo
python scripts/run_offline_replay.py
```

On Windows PowerShell, use `py` instead of `python` if that is how Python is installed. The runtime uses `pathlib`, argument-list subprocess calls, and `tempfile`; it does not depend on Bash, POSIX paths, or macOS utilities. Docker Desktop with the WSL 2 backend is the intended container environment on Windows.

The current release is a research prototype. The local checkpoint sandbox and replay pipeline are executable; the Docker sandbox, real model/provider integration, PostgreSQL adapter, frozen SWE-bench task manifest, and empirical Paper 1 datasets/results still need to be completed before final evaluation.

The repository can now launch a frozen SWE-bench slice through the vendored mini-SWE-agent and import its trajectories into the VERITAS action schema. See `research/DATASETS.md`; benchmark execution remains opt-in because it can download large Docker images and incur model cost.

The demo uses a local toy filesystem sandbox. It does not call provider models, Docker, or external services.

## Main Directories

- `src/veritas/actions`: typed contracts, action classes, permissions.
- `src/veritas/risk`: impact, calibration, verifier/recovery stats, RC-VoV.
- `src/veritas/verification`: deterministic and heuristic semantic falsification.
- `src/veritas/sandbox`: local checkpointable execution and Docker-facing stubs.
- `src/veritas/eval`: baselines, replay, metrics, power/stat helpers.
- `research`: preregistration, manifests, result folders.
- `future`: Paper 2 learning, security study, and API hardening tracks kept outside the Paper 1 path.
