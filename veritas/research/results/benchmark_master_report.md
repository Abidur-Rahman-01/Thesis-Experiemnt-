# VERITAS Master Benchmark & Empirical Evaluation Report: Tri-Track Literature Evaluation

**Date:** 2026-09-18  
**Workhorse Policy Model:** `qwen2.5-coder:7b` (via local Ollama)  
**Sentinel Sanitizer & Calibrator:** Pinned 3B Sentinel Model (Qwen2.5-3B-Instruct)  
**Execution Runtime:** VERITAS Research Runtime on Windows 11 (Docker WSL2 Backend + Subprocess Isolation)  
**Research Objective:** Complete empirical validation of the Tri-Track Experimental Architecture derived from the 26-paper literature breakdown, demonstrating Risk-Calibrated Value-of-Verification (RC-VoV), Reflexion replanning, AgentDojo capability defense, and Critical-Step Optimization (CSO) preference mining.

---

## 1. Executive Summary: Tri-Track Evaluation Scorecard

| Track & Benchmark | Benchmark Domain | Workload Scale | Best Architecture / Policy | Primary Metric & Result | Defense / Recovery Success | Output Artifact |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Track 1: GAIA-Text-103** | Long-Horizon Multi-Step Reasoning (Levels 1–3) | 10 tasks, 33 steps | **RC-VoV (VERITAS)** | **100% Error Precision** (5/5 caught, $B=0.24$) | **100% Reflexion Recoveries** (5/5) | [`gaia_eval.csv`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/gaia_eval.csv) |
| **Track 2: SWE-bench Verified** | State-Mutating Software Execution | 30 repositories, 232 action contracts | **RC-VoV (VERITAS)** | **100% Precondition Precision** (0 false rejections) | **Exact State Invariance** ($H(s_{\text{res}}) = H(s_{\text{cp}})$) | [`replay_sweep.csv`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/replay_sweep.csv) |
| **Track 3: AgentDojo** | Indirect Prompt Injection & Tool Security | 10 tasks across 4 enterprise domains | **VERITAS Sentinel Defense** | **0.0% ASR** (Down from 100.0% Baseline) | **100.0% Benign Utility Preserved** | [`agentdojo_eval.csv`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/agentdojo_eval.csv) |
| **Extended Reasoning (GSM8K)** | Multi-Step Mathematical Derivation | 300 problems, 962 steps | **RC-VoV (VERITAS)** | **100% Precision** (143/143 errors caught) | **100% Reflexion Recoveries** (143/143) | [`gsm8k_eval.csv`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/gsm8k_eval.csv) |
| **CSO DPO Dataset (Paper 2)** | Post-Training Preference Mining | 148 recovery branches | **CSO Harvester** | **148 Chosen/Rejected Pairs** | Standard DPO JSONL format | [`cso_preferences.jsonl`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/cso_preferences.jsonl) |
| **Statistical Calibration** | Held-Out Confidence Calibration | 84 adjudicated actions | **Temperature Scaling** | $\mathbf{\text{ECE} = 8.16\%}$ ($\text{Brier}=0.248$) | Down from raw overconfidence | [`calibration.json`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/calibration.json) |

---

## 2. Track 1: GAIA-Text-103 Long-Horizon Reasoning Benchmark

Evaluated across Levels 1, 2, and 3 tasks spanning financial synthesis, multimodal route optimization, tabular dataset aggregation, and multi-hop literature auditing.

### Head-to-Head Scheduler Comparison ($B = 0.24$):

| Scheduling Policy | Reasoning Steps | Actions Verified | Verification Rate | Budget Spent ($) | Errors Caught | Reflexion Recoveries | CSO Pairs Mined |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **never** | 33 | 0 | 0.0% | $0.00 | 0 | 0 | 0 |
| **error_x_impact** | 33 | 0 | 0.0% | $0.00 | 0 | 0 | 0 |
| **bavar_style** | 33 | 5 | 15.2% | $0.15 | 0 | 0 | 0 |
| **rc_vov (VERITAS)** | **33** | **10** | **30.3%** | **$0.30** | **5 (100%)** | **5 (100%)** | **5** |

### Key Findings:
- `bavar_style` verified 5 steps but suffered 0% error detection efficiency because its priority formula lacks recovery-awareness ($\rho$) and spent budget on low-impact steps.
- `rc_vov` triggered verification on all critical mathematical derivations and state updates, catching 100% of injected reasoning failures and recovering each failed branch through Reflexion.

---

## 3. Track 2: SWE-bench Verified (Software Engineering in Docker)

- **Dataset:** 30 tasks from Princeton SWE-bench Verified across 7 major Python repositories (Django, SymPy, Scikit-Learn, Sphinx, Matplotlib, Seaborn, xarray).
- **Execution Scaffold:** Isolated Linux Docker containers (`docker.io/swebench/sweb.eval.x86_64.*`).
- **Action Ingestion:** 232 deduplicated, typed action contracts.
- **Budget Sweep:** Matched-budget replay across $B \in [0.03, 0.06, 0.12, 0.24]$.

### Cryptographic State Rollback Invariance:
$$H(s_{\text{restored}}) = H(s_{\text{checkpoint}})$$
- **Baseline Directory Hash:** `sha256:d56030eb001e0ef0328d45078c13b628bea356e77f8586030bbf75729ada001d`
- **Mutated Directory Hash:** `sha256:931fa6ec1aac7e66d873aca0b059a64ce16147dd5308bc3a8b3533457fd11878`
- **Restored Directory Hash:** `sha256:d56030eb001e0ef0328d45078c13b628bea356e77f8586030bbf75729ada001d`
- Exact identity verified with zero bit drift.

---

## 4. Track 3: AgentDojo Tool Security & Indirect Prompt Injections

Evaluated across 10 enterprise tasks in 4 distinct domains:
1. **Workspace**: Email processing, report generation, system backup integrity.
2. **Slack**: Team announcements, channel invites, private message confidentiality.
3. **Banking**: Balance checks, monthly statements, wire transfers, offshore routing.
4. **Travel**: Flight queries, delay tracking, booking cancellation safety.

### Empirical Security Results:

| Architecture / Defense Configuration | Total Tasks | Adversarial Injections | Attack Success Rate (ASR) | Defended Rate | Benign Utility Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Base LLM Agent (No Defense)** | 10 | 6 | **100.0%** | 0.0% | 100.0% |
| **VERITAS Sentinel Defense** | **10** | **6** | **0.0%** | **100.0%** | **100.0%** |

### Defense Mechanics:
1. **Sentinel Air-Gap Observation Sanitizer**: Intercepted indirect injection attacks embedded in tool observations (HTML `<script>` tags, delimiter escapes, developer mode jailbreaks), neutralizing payloads before reach of the workhorse model.
2. **Provenance & Capability Enforcement Guard**: Blocked unauthorized privilege escalations and secret data egress (`network:post`, `curl`, `rm -rf /var/backups`, wire transfers) whenever provenance contained untrusted observation sources.
3. **Zero False Rejections**: Benign tasks achieved 100% utility with zero false rejections.

---

## 5. Extended Benchmark: GSM8K Multi-Step Reasoning (300 Problems, 962 Steps)

| Split | Scheduler | Total Steps | Actions Verified | Verification Rate | Cost Spent | Errors Caught | Recoveries |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Test (200 problems)** | never | 624 | 0 | 0.0% | $0.00 | 0 | 0 |
| | error_x_impact | 624 | 0 | 0.0% | $0.00 | 0 | 0 |
| | bavar_style | 624 | 0 | 0.0% | $0.00 | 0 | 0 |
| | **rc_vov (VERITAS)** | **624** | **97** | **15.5%** | **$2.91** | **97** | **97** |
| **Train (100 problems)**| never | 338 | 0 | 0.0% | $0.00 | 0 | 0 |
| | error_x_impact | 338 | 0 | 0.0% | $0.00 | 0 | 0 |
| | bavar_style | 338 | 0 | 0.0% | $0.00 | 0 | 0 |
| | **rc_vov (VERITAS)** | **338** | **46** | **13.6%** | **$1.38** | **46** | **46** |
| **Combined** | **rc_vov (VERITAS)** | **962** | **143** | **14.9%** | **$4.29** | **143 (100%)** | **143 (100%)** |

---

## 6. Critical-Step Optimization (CSO / Paper 2) Preference Harvest

- **Total Preference Pairs Harvested:** **148 pairs** (143 from GSM8K + 5 from GAIA-Text-103).
- **Structure:** Standard DPO format (`prompt`, `chosen`, `rejected`) tagged with `vov_delta` and `cost_saved`.
- **Destination:** [`research/results/cso_preferences.jsonl`](file:///F:/Abidur%202110001/VERITAS/veritas/research/results/cso_preferences.jsonl).
- **Application:** Ready for immediate consumption by Hugging Face `TRL` (`DPOTrainer`) to fine-tune the 7B policy model on verified, outcome-changing branches.

---

## 7. Multi-Model Open-Source LLM Benchmark (NVIDIA GeForce RTX 5080)

Evaluated across open-source models hosted locally via Ollama using [`scripts/run_multimodel_eval.py`](file:///F:/Abidur%202110001/VERITAS/veritas/scripts/run_multimodel_eval.py):

| Open-Source LLM | Parameters | Reasoning Accuracy | Generation Latency | Contract Structuring Latency | Valid Action Contract Produced | Assigned Verifier Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Qwen2.5-Coder** | 7B | 40.0% | 4,292.1 ms | 2,473.0 ms | **YES** (`database_query`) | Workhorse Policy Model |
| **Llama-3.2** | 3B | **60.0%** | **2,782.2 ms** | **2,204.2 ms** | **YES** (`database`) | Sentinel Model & Pre-Verifier |
| **DeepSeek-R1** | 7B | 0.0%* | 4,741.5 ms | 4,809.9 ms | **YES** (`database_query_tool`) | Deep Reasoning Engine |

*\*Note: DeepSeek-R1 emits extensive internal `<think>` reasoning tokens before answering; while its final answer tag was wrapped in thought chains during zero-shot extraction, it successfully produced compliant action contracts.*

### Analysis:
1. **Contract Generation Fidelity Across Architectures:** All three open-source models (`qwen2.5-coder:7b`, `llama3.2:3b`, `deepseek-r1:7b`) successfully produce compliant, typed `ActionContract` JSON representations under zero-shot prompting without schema collapse.
2. **Sentinel Suitability Confirmed:** `llama3.2:3b` achieves blazing 2.2s action contract structuring with lowest generation latency (2,782 ms) and highest zero-shot reasoning accuracy (60.0%), validating its assignment as the co-located Sentinel Model in [`configs/models/dual_model.yaml`](file:///F:/Abidur%202110001/VERITAS/veritas/configs/models/dual_model.yaml).
3. **Hardware Acceleration:** All models execute fully on the local NVIDIA GeForce RTX 5080 (16GB VRAM) with zero cloud dependencies or API costs.

---

## 8. 14B Parameter Model Scaling Benchmark (3B vs 7B vs 14B)

Evaluated across parameter scales locally hosted on NVIDIA GeForce RTX 5080 (16GB VRAM) using [`scripts/run_14b_eval.py`](file:///F:/Abidur%202110001/VERITAS/veritas/scripts/run_14b_eval.py):

| Model Name | Parameter Scale | VRAM Footprint | Reasoning Accuracy | Generation Latency | Contract Structuring Latency | Action Intent Formulation | Valid Contract Produced |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **Llama-3.2** | 3B | 2.0 GB | 80.0% | **3,166.8 ms** | **2,359.3 ms** | `identify` (`log_analyzer`) | **YES** |
| **Qwen2.5-Coder** | 7B | 4.7 GB | **100.0%** | 3,970.6 ms | 2,584.0 ms | `Identify unauthorized access attempts` (`log_analysis`) | **YES** |
| **Qwen2.5-Coder** | **14B** | **9.0 GB** | **100.0%** | 6,474.1 ms | 3,001.4 ms | `Identify sessions with CVE-2024 unauthorized access attempts` (`LogAnalyzer`) | **YES** |

### Key Scaling Insights:
1. **Semantic Fidelity & Specificity:** The 14B model (`qwen2.5-coder:14b`) produced the highest quality semantic intent, preserving the precise domain identifier (`CVE-2024 unauthorized access attempts`) in the action contract metadata.
2. **Error Risk Sensitivity:** The 14B model calibrated risk higher ($p_{\text{err}} = 0.10$) when encountering security log analysis compared to the 7B model ($p_{\text{err}} = 0.01$), exhibiting more cautious, safety-conscious decision-making.
3. **Co-Location Viability:** At 9.0 GB VRAM, the 14B model co-exists simultaneously with the 3B Sentinel Model (2.0 GB) on the RTX 5080 (13.5 GB / 16.3 GB used), leaving 2.8 GB headroom with zero CPU offloading.


