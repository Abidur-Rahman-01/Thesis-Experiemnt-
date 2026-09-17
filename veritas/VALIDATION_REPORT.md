# VERITAS Validation Report

Validation date: 2026-09-17

## Verdict

The repository is a working, platform-neutral Paper 1 prototype, but it is not yet research-runtime-ready or final-evaluation-ready under Appendix D of `VERITAS_updated_research_blueprint.md`.

The typed action path, permission checks, impact scoring, calibration utilities, RC-VoV equation, scheduler family, JSONL logging, local checkpoint/restore, replay engine, and toy end-to-end flow are implemented and tested. The current code contains no macOS-only runtime dependency.

## Automated Validation

| Check | Result |
| --- | --- |
| Unit, integration, and end-to-end tests | Pass: 28 tests |
| Python source parsing | Pass: 72 Python files |
| Bytecode compilation | Pass |
| RC-VoV randomized invariants | Pass: 10,000 generated inputs |
| Toy online trajectory | Pass |
| JSONL collection and replay | Pass |
| Checkpoint, mutation, restore, hash equality | Pass |
| Path traversal rejection | Pass |
| Tampered/external checkpoint rejection | Pass |
| Missing subprocess executable handling | Pass |
| Seeded random matched-budget reproducibility | Pass |
| Git whitespace check | Pass |

These checks were executed on the development host. Native Windows, Docker Desktop, CUDA, RTX 5080, model loading, and VRAM behavior cannot be certified without running on the target machine.

## Blueprint Coverage

| Area | Status | Notes |
| --- | --- | --- |
| Repository/module architecture | Implemented | Paper 1 and future tracks are separated. |
| Typed `ActionContract` | Implemented | Schema, classification, permissions, provenance. |
| RC-VoV equation | Implemented | Matches the expanded equation in Appendix A. |
| Required scheduler baselines | Prototype complete | Includes Error x Impact, BAVAR-style, random matched-budget, no-recovery and class-level RC-VoV. Published BAVAR fidelity still needs literature-level validation. |
| Local checkpoint/restore | Implemented | Hash round-trip and tamper checks pass. |
| Action/event JSONL | Implemented, incomplete fields | Core gate fields are logged; token counts, latency, environment-failure taxonomy, and final task outcome remain incomplete. |
| Calibration utilities | Implemented | Temperature scaling, Brier, NLL, ECE. No frozen empirical calibration split exists. |
| Verifier/recovery statistics | Scaffolded | Configuration values have zero observations/trials and must not support research claims yet. |
| Docker sandbox | Missing | `DockerSandbox` is an explicit unavailable stub; Compose currently provides PostgreSQL only. |
| Real policy/provider model | Missing | Only scripted policy and heuristic estimators/verifiers exist. |
| SWE-bench Verified runner | Adapter implemented; data pending | A frozen JSON manifest can launch the vendored mini-SWE-agent in Docker and its trajectories can be imported into VERITAS. The real task list is still empty and no benchmark run has been completed. |
| PostgreSQL | Optional stub | JSONL is the active equivalent store; PostgreSQL adapter is not implemented. |
| Frozen dependencies | Missing | No `uv.lock`; model revisions are placeholders. |
| Empirical datasets/results | Missing | No labeled action dataset, measured verifier statistics, recovery trials, budget curves, or online results. |
| Power analysis/final preregistration | Not complete | Helpers and draft documents exist; final sample-size evidence and frozen config do not. |

## Windows Target

The Python prototype uses `pathlib`, `tempfile`, `shutil`, and argument-list subprocess execution. It does not invoke Bash, use POSIX-only process APIs, or embed macOS paths. Use Python 3.10 or newer on Windows.

Recommended PowerShell smoke test:

```powershell
cd veritas
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e .
py -m unittest discover -s tests -v
py -m veritas --demo
py scripts\run_recovery_eval.py
py scripts\run_offline_replay.py
```

For the RTX 5080 phase, record `nvidia-smi`, Python, PyTorch/CUDA, Docker, model revision, quantization, context length, peak VRAM, and generation correctness exactly as required by Phase 1. Consumer Blackwell support varies by the selected PyTorch, CUDA, inference-server, and quantization versions, so GPU readiness cannot be inferred from hardware capacity alone.

## Blocking Work Before Research Claims

1. Implement and test the Docker sandbox with no network by default, CPU/RAM/time/output limits, and disposable workspaces.
2. Pin the Windows/Linux Python, model, CUDA, and inference dependencies and generate a lock file.
3. Integrate a competent primary policy and local verifier, then pass the policy viability gate.
4. Freeze a non-empty SWE-bench Verified task manifest and use the mini-SWE-agent bridge to run reproducible development trajectories.
5. Create adjudicated action labels without using execution success or verifier output as circular semantic ground truth.
6. Estimate calibration, class-level verifier statistics, and recovery statistics from held-out data with sample counts and uncertainty intervals.
7. Add missing logging fields and distinguish environment/tool failures from semantic action failures.
8. Run matched-budget offline curves, the recovery experiment, power analysis, and the preregistered online pilot.

Until those items are complete, the correct status is: **implementation prototype passes local tests; scientific and Windows GPU validation remain pending**.
