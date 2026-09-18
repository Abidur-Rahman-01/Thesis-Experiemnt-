# VERITAS Empirical Output Curves & Visual Analysis

This directory contains publication-grade figures, output curves, and reliability diagrams generated from verified benchmark evaluation runs.

## Index of Generated Figures

| Figure File | Format | Metric / Analysis | Benchmark / Track |
| :--- | :--- | :--- | :--- |
| [eritas_master_output_dashboard.png](figures/veritas_master_output_dashboard.png) | PNG (300 DPI) & SVG | Master 4-panel consolidated experimental dashboard | All Tracks (SWE-bench, GAIA, GSM8K, AgentDojo, Scaling) |
| [igure1_vov_budget_efficiency_curve.png](figures/figure1_vov_budget_efficiency_curve.png) | PNG (300 DPI) & SVG | Errors caught vs budget ( \in [0.03, 0.24]$) & cost efficiency | SWE-bench Verified |
| [igure2_calibration_reliability_curve.png](figures/figure2_calibration_reliability_curve.png) | PNG (300 DPI) & SVG | Reliability diagram (=x$), ECE reduction, Brier & NLL metrics | Statistical Calibration (84 actions) |
| [igure3_model_scaling_latency_curve.png](figures/figure3_model_scaling_latency_curve.png) | PNG (300 DPI) & SVG | Parameter scale vs latency (ms), tool accuracy, VRAM headroom | NVIDIA RTX 5080 (3B vs 7B vs 14B) |
| [igure4_security_and_recovery_frontier.png](figures/figure4_security_and_recovery_frontier.png) | PNG (300 DPI) & SVG | Indirect prompt injection defense (ASR) & Reflexion recovery | AgentDojo, GAIA-Text-103, GSM8K, SWE-bench |

---

## 1. Figure 1: Value-of-Verification Budget & Cost Efficiency Curve

- **X-Axis**: Verification budget fraction  \in [0.03, 0.06, 0.12, 0.24]$.
- **Y-Axis**: Total consequential errors caught.
- **Key Empirical Takeaway**: VERITAS RC-VoV selectively prioritizes outcome-critical and reversible actions, intercepting errors without exhausting the compute budget. Under matched budgets, baselines (BAVAR, static  	imes I_t$, never-verify) either fail to trigger or verify low-impact irreversible actions.
- **Precondition Precision**: VERITAS achieved **0 false rejections** across all tested budget thresholds.

---

## 2. Figure 2: Statistical Risk Calibration Reliability Diagram

- **Empirical Evaluation**: 84 adjudicated action steps evaluated against ground-truth execution outcomes.
- **Raw Prior**: Expected Calibration Error (ECE) = .36\%$, Brier Score = .347$, NLL = .074$.
- **Calibrated Prior (=10.0$)**: Expected Calibration Error (ECE) = $\mathbf{8.17\%}$ (a **.8\%$ relative drop**), Brier Score = $\mathbf{0.248}$, NLL = $\mathbf{0.690}$.
- **Reliability Curve**: The temperature-calibrated curve closely tracks the ideal diagonal identity line (=x$), ensuring that calculated value-of-verification $	ext{VoV}(a)$ reflects true operational risk.

---

## 3. Figure 3: Multi-Model Parameter Scaling Curve (RTX 5080)

- **Models**: llama3.2:3b (2.0 GB VRAM), qwen2.5-coder:7b (4.7 GB VRAM), qwen2.5-coder:14b (9.0 GB VRAM).
- **Latency Scaling**: Total end-to-end latency scales moderately from ,526$ ms (3B) to ,555$ ms (7B) to ,475$ ms (14B).
- **Tool Contract Accuracy**: Increases from .0\%$ (3B) to .0\%$ (7B & 14B).
- **Hardware Headroom**: RTX 5080 (16,303 MiB VRAM) comfortably co-locates the 3B Sentinel + 14B Workhorse with .0$ GB of free VRAM headroom at 42°C.

---

## 4. Figure 4: Security & Cross-Benchmark Autonomous Recovery Frontier

- **AgentDojo Prompt Injection Defense**:
  - Base LLM Agent: Attack Success Rate (ASR) = .0\%$, Defended Rate = .0\%$.
  - VERITAS Sentinel: Attack Success Rate (ASR) = $\mathbf{0.0\%}$, Defended Rate = $\mathbf{100.0\%}$, Benign Utility = $\mathbf{100.0\%}$.
- **Reflexion Counterfactual Recovery**:
  - GAIA-Text-103: .0\%$ recovery rate (/5$ injected errors repaired).
  - GSM8K Logic: .0\%$ recovery rate (/49$ calculation slips caught and repaired).
  - SWE-bench Verified: Exact cryptographic hash invariance (s_{restored}) = H(s_{checkpoint})$.
