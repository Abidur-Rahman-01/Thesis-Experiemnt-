---
marp: true
theme: default
paginate: true
header: "VERITAS Pre-Defense | Risk-Calibrated Selective Verification"
footer: "Department of Computer Science & Engineering | Thesis Pre-Defense"
style: |
  section {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1e293b;
    background-color: #f8fafc;
    padding: 40px 60px;
  }
  h1 { color: #0f172a; font-weight: 800; font-size: 2.1rem; margin-bottom: 0.4rem; }
  h2 { color: #1e3a8a; font-weight: 700; font-size: 1.5rem; margin-top: 0; }
  h3 { color: #334155; font-size: 1.15rem; }
  blockquote {
    background: #e0e7ff;
    border-left: 6px solid #4338ca;
    padding: 10px 16px;
    border-radius: 4px;
    font-size: 0.95rem;
  }
  code {
    background: #e2e8f0;
    color: #0f172a;
    font-size: 0.85em;
    padding: 2px 6px;
    border-radius: 4px;
  }
  pre code {
    background: #0f172a;
    color: #f8fafc;
    padding: 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    line-height: 1.35;
  }
  table {
    font-size: 0.82rem;
    border-collapse: collapse;
    width: 100%;
  }
  th, td {
    border: 1px solid #cbd5e1;
    padding: 6px 10px;
    text-align: left;
  }
  th {
    background-color: #e2e8f0;
    color: #0f172a;
  }
  .highlight {
    color: #2563eb;
    font-weight: 700;
  }
  .kpi-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
    border-radius: 8px;
    padding: 14px;
    margin: 6px 0;
  }
---

<!-- Slide 1: Title Slide -->
# VERITAS
## Risk-Calibrated, Budget-Aware Verification and Counterfactual Recovery for State-Mutating LLM Agents

**Thesis Pre-Defense Presentation**

- **Candidate:** Abidur Rahman Sadik
- **Focus Area:** Trustworthy Autonomous LLM Agents, Selective Verification & Decision Theory
- **Hardware Profile:** Intel Core i9-class CPU, NVIDIA RTX 5080 (16 GB VRAM), 128 GB RAM
- **Primary Research Scope:** Resource-bounded verification for software and tool-using agents

---

### Speaker Notes (Slide 1)
"Respected members of the committee, welcome to my thesis pre-defense. Today I present VERITAS: Risk-Calibrated, Budget-Aware Verification and Counterfactual Recovery for State-Mutating LLM Agents. In this presentation, I will establish the core theoretical problem of resource-bounded agent verification, present our end-to-end architecture, review our working prototype and property validation, and outline the rigorous empirical campaign I will execute between today's pre-defense and the final thesis defense."

---

<!-- Slide 2: Context & Motivation -->
# 1. Context & Motivation: The Rise of State-Mutating Agents

Autonomous LLM agents are increasingly deployed for **long-horizon, state-mutating workflows**:
- Automated software maintenance (SWE-bench, fixing security regressions).
- Command-line system administration (Bash, Docker, package installations).
- Database migrations and external API interactions.

### The Fundamental Asymmetry of Tool Actions
Not all tool actions carry equal danger or reversibility:

| Action Category | Example | Reversibility | Impact Level |
| :--- | :--- | :--- | :--- |
| **Passive / Inspect** | `cat file.py`, `ls -la`, `grep` | Deterministically zero side-effect | Negligible ($I_t \approx 0.0$) |
| **Local Mutation** | `git checkout -b`, editing test cases | High (local git rollback) | Moderate ($I_t \approx 0.3$) |
| **Destructive / External** | `rm -rf`, `git push --force`, DB drop | Irreversible / blast radius | Critical ($I_t \ge 0.8$) |

> **Insight:** Treating all agent decisions uniformly is computationally wasteful and practically hazardous.

---

### Speaker Notes (Slide 2)
"To motivate our work, look at modern autonomous software agents. When an agent acts in a real repository, steps are fundamentally asymmetric. Reading a file has zero persistent consequence. Modifying a test file has local, reversible impact. But running a destructive bash command or pushing broken code can permanently corrupt state. Today's systems either verify indiscriminately or fail silently because they treat all steps as equals."

---

<!-- Slide 3: The Verification Dilemma -->
# 2. The Verification Dilemma: The Failure of Extremes

Existing LLM agent paradigms fall into two problematic extremes:

```
[ Zero Verification (Fast & Fragile) ]  <=================>  [ Always-Verify / Reflexion (Safe & Unusable) ]
  • High speed & low token cost                                • Huge compute & latency overhead (3x-10x)
  • Errors compound catastrophically                            • Verifier noise: False rejections halt valid runs
  • Silent failures corrupt execution state                     • Exceeds inference token and financial budgets
```

### The Core Scientific Dilemma
Verification compute is a **scarce, costly resource**:
1. Verifying every step exhausts API and inference budgets rapidly.
2. Verifiers themselves are imperfect: they exhibit false alarms ($f_t$) and detection misses ($1 - d_t$).
3. **The Core Question:** *Can an agent mathematically decide WHEN to spend verification compute, guided by error probability, action impact, verifier operating power, and rollback capability?*

---

### Speaker Notes (Slide 3)
"This creates a scientific dilemma. A naive agent that never verifies is fast and cheap, but brittle—a single wrong edit can derail a 30-step trajectory. Conversely, existing reflective architectures like Reflexion or step-level LLM judges verify almost every step. That is computationally prohibitive: it triples or quintuples inference cost and introduces verifier errors. If a verifier has a 10% false alarm rate, verifying 20 steps almost guarantees a valid trajectory gets prematurely killed. We need selective verification."

---

<!-- Slide 4: Research Questions -->
# 3. Primary Research Questions & Hypotheses

> **Primary Research Question:**
> *Under a fixed verification compute budget, can a risk-calibrated value-of-verification controller catch more consequential state-mutating errors than standard uncertainty-only, impact-only, and simple product policies?*

- **RQ1 (Calibration Viability):** Can step-level action failure probabilities $p_{e,t}$ be reliably calibrated in agentic tool-use loops using held-out temperature/isotonic scaling?
- **RQ2 (Budgeted Allocation):** Does selective gating catch significantly more consequential errors per unit compute than uniform or random budget-matched baselines?
- **RQ3 (Theoretical Value-Add):** Does the complete decision-theoretic RC-VoV formulation beat the mandatory product baseline:
  $$v_t = \mathbf{1}[p_{e,t} I_t > \tau_{\mathrm{PI}}]?$$
- **RQ4 (Counterfactual Recovery):** Does restoring to local transactional checkpoints with counterfactual continuation significantly lower residual loss $\rho_t$ compared to restarting from step 0?

---

### Speaker Notes (Slide 4)
"Here are the research questions defining my thesis. Notice RQ3 in particular: this is our pre-registered falsification criterion. If our full decision-theoretic formulation cannot beat a simple product of calibrated error probability times action impact, then the extra mathematical complexity is unjustified. This ensures our thesis makes a genuine scientific claim rather than building an elaborate engineering wrapper."

---

<!-- Slide 5: Literature Landscape -->
# 4. Research Positioning & Competitive Landscape

```
                     ┌─────────────────────────────────────────────────────────┐
                     │              Autonomous Agent Research                  │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
          ┌───────────────────────────────────────┼───────────────────────────────────────┐
          ▼                                       ▼                                       ▼
  Reflective Agents                       Agent Security & Guardrails             Budgeted Inference
  (Reflexion, ReVISE)                     (GuardAgent, AgentDojo)                 (BAVAR, Cost-MDPs)
  • Verifies post-execution               • Binary security policy filtering       • Formulates compute trade-offs
  • No action-impact modeling             • Ignores execution rollback value       • Assumes synthetic error rates
  • Ignores compute budget                • Treats all tools symmetrically         • Lacks recovery modeling
          │                                       │                                       │
          └───────────────────────────────────────┼───────────────────────────────────────┘
                                                  ▼
                                     ┌─────────────────────────┐
                                     │         VERITAS         │
                                     └─────────────────────────┘
                                     • Decision-Theoretic RC-VoV
                                     • Typed Action Contracts
                                     • Calibrated Error Probabilities
                                     • Transactional Checkpoints
                                     • Offline Matched-Budget Replay
```

---

### Speaker Notes (Slide 5)
"We position VERITAS at the intersection of three active subfields: reflective self-correction (like Reflexion), agent security guardrails (like GuardAgent and AgentDojo), and budget-aware reasoning (like BAVAR). While prior work solves pieces of this puzzle, none combine calibrated error probability, multidimensional action impact, empirical verifier sensitivity, and rollback recovery value into a single, resource-bounded control policy."

---

<!-- Slide 6: End-to-End System Architecture -->
# 5. End-to-End System Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │             1. Policy Model (Frontier / 8B)             │
                  └───────────────────────────┬────────────────────────────┘
                                              │ Proposes action a_t
                                              ▼
                  ┌────────────────────────────────────────────────────────┐
                  │        2. Action Contract & Permission Boundary        │
                  │   • Schema check • Path traversal • Permission policy   │
                  └───────────┬────────────────────────────────────────────┘
                              │ Validated ActionContract
                              ▼
        ┌──────────────────────────────────────────────────────────┐
        │               3. Risk & Calibration Engine               │
        │   • Logit / Feature Estimator → Temperature Scale → p_e  │
        │   • Multi-Attribute Impact Scorer → I_t                  │
        │   • Empirical Verifier / Recovery Tables (d_t, f_t, rho) │
        └─────────────────────────────┬────────────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │            4. RC-VoV Dynamic Budget Controller           │
        │      Compute Delta_t & Marginal Utility m_t >= lambda_t   │
        └──────────────┬────────────────────────────┬──────────────┘
                       │ VERIFY                     │ SKIP
                       ▼                            │
        ┌──────────────────────────────┐            │
        │ 5. Action Falsification      │            │
        │    (Deterministic + Semantic)│            │
        └──────────────┬───────────────┘            │
                       │ Pass                       │
                       ▼                            ▼
        ┌──────────────────────────────────────────────────────────┐
        │      6. Transactional Execution & Checkpoint Engine       │
        │   • Snapshot workspace hash • Execute in Sandbox         │
        │   • Catch failure → Rollback to safe checkpoint           │
        └─────────────────────────────┬────────────────────────────┘
                                      │
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │          7. Structured JSONL Trajectory Logging           │
        │     Full state, logits, p_e, impact, decisions, costs    │
        └──────────────────────────────────────────────────────────┘
```

---

### Speaker Notes (Slide 6)
"This is the end-to-end architecture of VERITAS. The runtime operates as a 7-stage pipeline: First, the policy proposes a typed action. Second, the action contract and permission boundary deterministically validate parameters. Third, the risk and calibration engine estimates calibrated error probability and multi-attribute impact. Fourth, the RC-VoV controller decides whether to verify or skip based on remaining budget. Fifth, if verified, falsification tests are executed. Sixth, mutating actions are executed with transactional checkpoint rollback. Finally, complete decision records are logged for offline matched-budget replay."

---

<!-- Slide 7: Architecture Deep Dive - Action Contracts & Impact -->
# 6. Architecture Deep Dive: Typed Contracts & Impact Scoring

### 1. The `ActionContract` Schema
Every proposed action is strictly typed with operational metadata:
- **Action Class:** `inspect`, `code_edit`, `shell`, `destructive_filesystem`, `external_mutation`.
- **Preconditions & Postconditions:** Deterministically checkable state predicates.
- **Rollback Capability:** Can the environment snapshot and restore this change?

### 2. Multi-Dimensional Action Impact Vector ($I_t$)
Impact is not a vague heuristic; it is a normalized linear combination:
$$x_t = \begin{bmatrix} x_{\text{mutation}} & x_{\text{irreversible}} & x_{\text{privilege}} & x_{\text{external}} & x_{\text{secret}} & x_{\text{untrusted}} & x_{\text{scope}} \end{bmatrix}^\top \in [0, 1]^7$$

$$I_t = \operatorname{clip}(w^\top x_t, 0, 1)$$

### 3. Hard-Critical Override Gate
Certain operations cannot be bypassed regardless of model confidence:
$$\text{hard-critical}_t = \mathbf{1}[\text{destructive\_fs} \lor \text{credential\_access} \lor \text{git push --force}]$$

---

### Speaker Notes (Slide 7)
"Let's look deeper into the contract and impact layer. In traditional agents, tool use is just raw strings passed to a bash subprocess. In VERITAS, every action is an ActionContract with explicit schemas and rollback declarations. The impact model calculates an impact score between 0 and 1 across seven explicit dimensions: mutation, irreversibility, privilege level, external side-effects, secret exposure, untrusted data flow, and blast-radius scope. Furthermore, hard-critical operations like deleting directories or credential access immediately force verification, regardless of what the model estimates."

---

<!-- Slide 8: Mathematical Core - RC-VoV Formulation -->
# 7. Mathematical Core: Risk-Calibrated Value-of-Verification

### The Expected Loss Equations
- **Expected loss without verification:**
  $$L_t^{\text{no-verify}} = p_{e,t} I_t$$

- **Expected loss with verification:**
  $$L_t^{\text{verify}} = C_{v,t} + p_{e,t} \underbrace{[(1 - d_t) I_t + d_t \rho_t I_t]}_{\text{Missed error + Detected error with residual recovery loss}} + \underbrace{(1 - p_{e,t}) f_t C_{fp,t}}_{\text{False alarm penalty}}$$

### The Master RC-VoV Equation
Expected net value of verifying action $a_t$:
$$\Delta_t = L_t^{\text{no-verify}} - L_t^{\text{verify}}$$

$$\boxed{\Delta_t = \underbrace{p_{e,t} d_t (1 - \rho_t) I_t}_{\text{Expected Avoided Loss}} - \underbrace{C_{v,t}}_{\text{Verification Cost}} - \underbrace{(1 - p_{e,t}) f_t C_{fp,t}}_{\text{Cost of False Rejection}}}$$

---

### Speaker Notes (Slide 8)
"Slide 8 is the theoretical core of the thesis. Let's analyze the RC-VoV equation term by term. The first term is the expected avoided loss: error probability $p_{e,t}$ times verifier sensitivity $d_t$, times recovery effectiveness $(1 - \rho_t)$, times impact $I_t$. If an error cannot be recovered—meaning $\rho_t = 1$—the avoided loss is zero, so verification is pointless! The second term is the direct compute cost of verification $C_{v,t}$. The third term is the expected penalty of a false alarm: the probability the action was correct, times false rejection rate $f_t$, times false positive cost $C_{fp,t}$. Verification is only selected if $\Delta_t > 0$."

---

<!-- Slide 9: Dynamic Budget Controller & Baselines -->
# 8. Dynamic Budget-Aware Gating & Mandatory Baselines

### Marginal Value per Verification Dollar
Given total budget $B_0$ and remaining budget $B_t$:
$$m_t = \frac{\max(\Delta_t, 0)}{C_{v,t} + \epsilon}$$

### Adaptive Verification Gate
Verification is triggered if:
$$v_t = \mathbf{1}\left[\text{hard-critical}_t \lor (m_t \ge \lambda_t)\right], \quad \text{where } \lambda_t = \lambda_0 \left[1 + \kappa \left(1 - \frac{B_t}{B_0}\right)\right]$$
As budget depletes ($B_t \to 0$), the acceptance threshold $\lambda_t$ automatically rises.

### The Mandatory Falsifiable Baselines
To justify RC-VoV, it must beat these baselines under **identical verification compute**:
1. **$p_e \times I$ Baseline:** $v_t = \mathbf{1}[p_{e,t} I_t > \tau_{\mathrm{PI}}]$ (simple product threshold).
2. **BAVAR-Style Expected Value:** Resource-constrained value scheduler without rollback.
3. **Random Budget-Matched:** Random selection matching exact token spend.

---

### Speaker Notes (Slide 9)
"To enforce a hard compute budget, we evaluate the marginal value per unit verification cost. The controller dynamically raises the acceptance threshold lambda as the budget burns down. Most importantly, we establish the mandatory $p_e \times I$ baseline. Prior literature often compared complex systems against naive 'always-verify' or random baselines. In VERITAS, our primary comparison is against a calibrated error probability multiplied by action impact. If our full RC-VoV formulation cannot beat this simple product, we will simplify our decision rule."

---

<!-- Slide 10: Checkpointing & Counterfactual Recovery Architecture -->
# 9. Architecture Deep Dive: Checkpoint & Recovery Engine

```
       Step t-1                Step t (Proposed Mutation)               Step t+1
    [ Safe State ] ───► [ Checkpoint Snapshot (SHA-256) ]
                                      │
                                      ▼ Execute Action a_t
                             [ Sandbox Evaluation ]
                                ├── Success ──► Advance state
                                └── Failure / Falsified
                                      │
                                      ▼
                        [ Transactional Rollback ]
                                      │
                         Restore filesystem to SHA-256 state
                                      │
                                      ▼
                      [ Counterfactual Continuation ]
                         Branch alternative action a'_t
```

- **Local Snapshot Hash:** SHA-256 cryptographic verification of workspace state.
- **Rollback Guarantee:** Clean revert of file trees without restarting multi-step agent trajectories.
- **Empirical Recovery Metric ($\rho_t$):** Residual task degradation after rollback vs cold restart.

---

### Speaker Notes (Slide 10)
"Slide 10 presents our checkpoint and recovery architecture. Traditional agents have no transactional memory: if a tool causes a fatal syntax error or corrupts a configuration 15 steps into a task, the agent either wanders blindly or restarts from step zero, burning 15 steps of compute. In VERITAS, whenever a state-mutating action is scheduled, the runtime takes a lightweight workspace snapshot validated by SHA-256 hashes. If the action is falsified or fails during execution, we perform a clean rollback to the nearest safe checkpoint and prompt for an alternative action branch."

---

<!-- Slide 11: Work Completed So Far - Working Prototype -->
# 10. Work Completed So Far: The VERITAS Prototype

We have implemented the full research architecture in `veritas/`:

<div class="kpi-box">

### Implementation Statistics (Validated as of September 2026)
- **Codebase:** 72 modular Python source files; zero platform-locked dependencies.
- **Action Subsystem:** Full `ActionContract`, permission boundary, and taxonomy parser.
- **Risk Subsystem:** Multi-attribute impact scorer, temperature calibrator, RC-VoV engine.
- **Recovery Subsystem:** Local checkpoint/restore manager with hash validation & tamper checks.
- **Evaluation Subsystem:** 6 baseline schedulers, offline replay engine, power analysis tools.
- **Storage Subsystem:** Complete JSONL trajectory and event logging engine.

</div>

### Automated Test Certification
| Validation Check | Result | Verification Scope |
| :--- | :--- | :--- |
| **Unit & Integration Suite** | **PASS (21/21 tests)** | Core loop, permissions, schedulers, hash verification |
| **RC-VoV Invariants** | **PASS (10,000 samples)** | Property-based randomized fuzzing across edge cases |
| **Tamper & Traversal Checks** | **PASS** | Path traversal rejection, hash mismatch rollback abort |
| **Toy Trajectory Replay** | **PASS** | Synthetic offline budget sweep across 5 budget tiers |

---

### Speaker Notes (Slide 11)
"I am pleased to report that the foundational architecture is not just a concept—it is a working, tested prototype. As certified in our validation report, the repository contains 72 Python modules covering contracts, calibration, the RC-VoV solver, checkpoint management, and offline replay. Our test suite passes all 21 unit and integration tests, as well as 10,000 randomized property-based invariant checks testing edge cases in the mathematical equations."

---

<!-- Slide 12: Offline Replay Architecture -->
# 11. Architecture Deep Dive: Offline Matched-Budget Replay

Online agent evaluation is slow and expensive. How do we test 10 schedulers fairly?

```
                        [ Single Expensive Logging Pass ]
                    Frontier Policy Runs Benchmark Trajectories
                                       │
                                       ▼
                   [ Action Event Logs (actions.jsonl) ]
                   • Action contract & features x_t
                   • Raw error score z_t & calibrated p_e
                   • Action impact I_t & estimated cost C_v
                   • Verifier verdict & ground truth label Y_t
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
           [ Budget Sweep: B = 10% ]             [ Budget Sweep: B = 50% ]
           Replay through Schedulers:            Replay through Schedulers:
           • Confidence threshold                • Confidence threshold
           • Error x Impact (p_e * I)            • Error x Impact (p_e * I)
           • BAVAR-style                         • BAVAR-style
           • RC-VoV                              • RC-VoV
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                     [ Comparative Allocation Curves ]
              Consequential Errors Caught vs Verification Spend
```

---

### Speaker Notes (Slide 12)
"Slide 12 explains our offline replay architecture, which solves the high financial and compute cost of evaluating multiple agent schedulers. Running 500 SWE-bench tasks across 8 schedulers online would cost tens of thousands of dollars and weeks of GPU time. Instead, we execute one comprehensive logging pass with our policy model, capturing rich action records. We then feed these identical logged decisions through our replay engine across different budget tiers, comparing exactly which actions each scheduler chooses to verify."

---

<!-- Slide 13: What I Am Going To Do - Overview -->
# 12. "What I Am Going to Do": The Pre-Defense Empirical Roadmap

To complete the thesis requirements for final defense, I will execute a **5-Phase Empirical Research Campaign**:

```
 [ Phase 1: Infrastructure ] ──► [ Phase 2: Trajectory Logging ] ──► [ Phase 3: Calibration & Stats ]
   • RTX 5080 vLLM Serving         • SWE-bench Verified Subset         • Held-out Temperature Scaling
   • Hardened Docker Sandbox       • Frontier Policy Execution         • Empirical d_t, f_t, rho_t
                                                                                 │
 ┌───────────────────────────────────────────────────────────────────────────────┘
 ▼
 [ Phase 4: Matched-Budget Replay ] ──► [ Phase 5: Online Evaluation & Power ]
   • Sweep budgets (0% to 100%)           • Statistical Power Sample Sizing
   • Test RC-VoV vs p_e * I               • End-to-End Task Success on Top-3
   • Evaluate Preregistered Stop Rule     • Final Thesis Writeup & Code Release
```

---

### Speaker Notes (Slide 13)
"Now, let us turn to the heart of the pre-defense: What I am going to do between now and the final defense. I have broken down the remaining work into five disciplined phases: Phase 1 validates the local hardware compute stack and Docker isolation. Phase 2 gathers trajectories from SWE-bench Verified. Phase 3 performs rigorous empirical calibration. Phase 4 runs our matched-budget replay sweeps to test our core hypothesis. Phase 5 executes the final power-sized online evaluation."

---

<!-- Slide 14: Phase 1 & 2 - Hardware, Sandbox & Benchmark Setup -->
# 13. Phase 1 & 2: Compute Infrastructure & Benchmark Manifest

### Phase 1: Hardware & Sandbox Isolation
- **Hardware Stack:** Reference RTX 5080 (16 GB VRAM) running local verifier/error estimator (Qwen2.5-Coder-7B-Instruct or Llama-3.1-8B-Instruct).
- **VRAM Constraint:** Enforce operational safety margin:
  $$M_{\text{peak}} \le 0.90 \times M_{\text{VRAM}} \quad (\le 14.4 \text{ GB})$$
- **Hardened Docker Sandbox:** Implement disposable Linux container execution with no network access, CPU/RAM quotas, and strict process timeouts.

### Phase 2: Benchmark & Trajectory Collection
- **Benchmark:** SWE-bench Verified (curated, non-circular real-world GitHub issues).
- **Policy Model:** Decoupled frontier policy (Claude 3.5 Sonnet / GPT-4o / Qwen-2.5-Coder-32B) to guarantee competent baseline trajectories.
- **Ground Truth Adjudication:** Human and test-suite ground truth labels ($Y_t \in \{0, 1\}$) recorded without circular dependency on the verifier.

---

### Speaker Notes (Slide 14)
"In Phase 1, we validate our local compute environment. We utilize our RTX 5080 GPU for the local verifier model while enforcing a strict memory limit of 90% peak VRAM. We also complete the Docker sandbox to isolate tool execution. In Phase 2, we decouple the policy model from the verifier: we use a frontier policy on a curated subset of SWE-bench Verified. This guarantees that the agent actually makes meaningful progress and generates realistic error distributions rather than failing at step 1."

---

<!-- Slide 15: Phase 3 - Empirical Calibration & Parameter Estimation -->
# 14. Phase 3: Calibration & Empirical Parameter Estimation

We do not assume verifier sensitivity or recovery rates are known; we **measure them**:

### 1. Calibration via Held-Out Temperature Scaling
- Minimize negative log-likelihood (NLL) on a frozen calibration split ($N_{\text{cal}} \ge 300$ actions):
  $$T^* = \operatorname*{arg\,min}_{T > 0} -\sum_{i=1}^{N_{\text{cal}}} \left[ y_i \log \sigma\left(\frac{z_i}{T}\right) + (1 - y_i) \log\left(1 - \sigma\left(\frac{z_i}{T}\right)\right) \right]$$
- Report Brier Score and Expected Calibration Error (ECE) before and after calibration.

### 2. Empirical Verifier & Recovery Statistics per Action Class
- **Detection Rate ($d_t$):** Measured empirical true positive rate of falsifier on labeled bugs.
- **False Positive Rate ($f_t$):** Measured false rejection rate on valid actions.
- **Residual Recovery Loss ($\rho_t$):** Measured empirical task penalty after rollback and continuation:
  $$\rho_t = 1 - \frac{\text{Success Rate}_{\text{after rollback}}}{\text{Success Rate}_{\text{clean baseline}}}$$

---

### Speaker Notes (Slide 15)
"Phase 3 addresses a critical scientific gap in prior agent literature. Many papers plug hypothetical constants into decision equations. In VERITAS, every parameter is empirically grounded. We fit temperature scaling on a held-out calibration split to guarantee that when the model outputs a 40% error probability, it truly means 40%. Furthermore, detection rate d, false alarm rate f, and recovery factor rho are computed directly from held-out trials across each action class."

---

<!-- Slide 16: Phase 4 - Matched-Budget Replay & Stop Rule -->
# 15. Phase 4: Matched-Budget Replay & The Stop Rule

### Matched-Budget Verification Curves
We evaluate all schedulers across identical action traces under fixed compute budgets:
$$\mathcal{B} \in \{0\%, 10\%, 20\%, 35\%, 50\%, 75\%, 100\% \text{ of full verification spend}\}$$

<div class="kpi-box">

### Primary Evaluation Metric
$$\text{Allocation Efficiency} = \frac{\text{Consequential Errors Caught}}{\text{Verification Compute Tokens / Cost Spent}}$$

</div>

### The Preregistered Stop Rule
> **Falsification Contract:**
> If RC-VoV does not achieve statistically significant higher allocation efficiency than the simple product baseline $p_{e,t} I_t$ on the held-out replay dataset:
> 1. We will **simplify the controller** rather than building unneeded engineering layers.
> 2. We will analyze why the additional terms ($d_t, f_t, \rho_t$) collapsed and report the finding honestly.

---

### Speaker Notes (Slide 16)
"Phase 4 is where we test our core hypothesis. We plot allocation curves across budget tiers from 0 to 100 percent. Our primary metric is consequential errors caught per unit verification compute. We have formally pre-registered a stop rule: if RC-VoV cannot statistically beat the simple product baseline $p_e \times I$, we will not hide the negative result. We will simplify the controller and document why the higher-order terms collapsed. This scientific rigor protects the integrity of the thesis."

---

<!-- Slide 17: Phase 5 - Controlled Recovery & Online Evaluation -->
# 16. Phase 5: Controlled Recovery & Online Task Evaluation

### Controlled Counterfactual Recovery Experiment
We isolate and quantify the exact value of transactional rollback:
- **Condition A (No Recovery):** Action failure terminates or blindly continues trajectory.
- **Condition B (Cold Restart):** Trajectory restarts from step 0.
- **Condition C (VERITAS Checkpoint Rollback):** Revert to step $t-1$ snapshot; branch continuation.
- **Hypothesis:** Condition C preserves $>70\%$ of spent tokens while maintaining final task resolution.

### Statistical Power Analysis & Online Benchmark
- Run a 30-task pilot to estimate error variance and effect sizes.
- Size the final online sample size $N$ using power analysis ($\beta = 0.20, \alpha = 0.05$):
  $$N \ge \frac{2(z_{\alpha/2} + z_{\beta})^2 \sigma^2}{\delta^2}$$
- Deploy the **Top-3 Schedulers** (RC-VoV, $p_e \times I$, and Best Baseline) for online end-to-end evaluation on SWE-bench Verified.

---

### Speaker Notes (Slide 17)
"In Phase 5, we execute two critical experiments. First, a controlled counterfactual recovery ablation: we compare checkpoint rollback against cold restarting and blind continuation, measuring token savings and task preservation. Second, rather than picking an arbitrary number of benchmark tasks, we run a 30-task pilot to conduct a formal statistical power analysis. This determines the exact sample size needed to detect significant differences in online task success and verification cost."

---

<!-- Slide 18: Research Timeline & Milestones -->
# 17. Thesis Execution Timeline to Final Defense

```
2026-Q3 (Current)            2026-Q4                       2027-Q1                 2027-Q2
 [ Pre-Defense ]      [ Data & Calibration ]         [ Replay & Recovery ]     [ Final Defense ]
        │                       │                             │                       │
        ▼                       ▼                             ▼                       ▼
  • Prototype validated   • Docker sandbox ready        • Replay budget sweep   • Online evaluation
  • Invariant tests pass  • SWE-bench traces logged     • Controlled recovery   • Final thesis writeup
  • Roadmap frozen        • Calibrator & stats fit      • Power analysis pilot  • Open-source release
```

| Milestone | Deliverable | Target Date | Status |
| :--- | :--- | :--- | :--- |
| **M0** | Architecture, prototype & invariant test suite | September 2026 | **COMPLETED** |
| **M1** | Docker sandbox & RTX 5080 inference service | October 2026 | In Progress |
| **M2** | Trajectory collection & adjudicated action labels | November 2026 | Planned |
| **M3** | Calibration, empirical stats & offline replay sweep | December 2026 | Planned |
| **M4** | Controlled recovery study & online pilot | January 2027 | Planned |
| **M5** | Final online benchmark & thesis defense draft | February 2027 | Planned |

---

### Speaker Notes (Slide 18)
"Here is our project timeline leading to the final defense. Milestone 0 is fully complete: the architecture, prototype, and invariant test suite are validated. Over the next two months, we complete the Docker sandbox and gather trajectories. By December, empirical calibration and the offline replay sweeps will be concluded. In early 2027, we run the controlled recovery study and online evaluation, leading directly into final thesis writeup and defense."

---

<!-- Slide 19: Risk Management & Pitfalls -->
# 18. Risk Analysis, Pitfalls & Mitigation Strategies

| Potential Risk | Severity | Scientific Mitigation Strategy |
| :--- | :---: | :--- |
| **$p_e \times I$ matches RC-VoV** | High | Treat as a valid scientific finding. Publish that action impact and calibrated uncertainty dominate higher-order verifier terms; simplify decision rule. |
| **Verifier Memory OOM on RTX 5080** | Medium | Maintain BF16 / AWQ fallback; offload policy model to external API while keeping verifier strictly local; enforce $M_{\text{peak}} \le 0.90 V_{\text{RAM}}$. |
| **Low Action Error Prevalence in Benchmark** | Medium | Filter SWE-bench subset for tasks with high state mutation frequency (multi-file modifications, complex dependency setups). |
| **Circular Ground Truth in Trajectory Labels** | High | Strictly decouple semantic correctness labels from execution return codes and verifier outputs using dual-annotator adjudication. |

---

### Speaker Notes (Slide 19)
"Every strong research proposal must account for risk. The largest scientific risk is that the simple product baseline $p_e \times I$ matches our full RC-VoV formulation. If that happens, it is not a project failure—it is an important scientific finding demonstrating that impact and uncertainty dominate verifier noise in practical agent loops. On the engineering side, we mitigate GPU memory risks through quantized local verifiers and API-based policy decoupling, and we prevent circular ground truth by keeping evaluation labels independent of verifier outputs."

---

<!-- Slide 20: Expected Contributions & Conclusion -->
# 19. Expected Contributions & Summary

### 1. Theoretical Contribution
A grounded **decision-theoretic framework (RC-VoV)** that unifies calibrated error estimation, multi-dimensional action impact, verifier sensitivity, and rollback recovery under explicit resource bounds.

### 2. Empirical Contribution
The first **falsifiable, matched-budget study** comparing selective verification policies against the mandatory $p_{e,t} I_t$ baseline, accompanied by a controlled evaluation of counterfactual recovery value.

### 3. Practical Artifact Contribution
A clean, tested, platform-neutral **open-source agent verification runtime** featuring typed action contracts, transactional local checkpoints, and complete offline replay capabilities.

---

### Thank You!
**Questions & Discussion**
- Codebase: `github.com/Abidur-Rahman-01/Thesis-Experiemnt-`
- Blueprint & Documentation: `VERITAS_updated_research_blueprint.md`

---

### Speaker Notes (Slide 20)
"In conclusion, VERITAS provides a principled, falsifiable framework for making autonomous LLM agents trustworthy without rendering them prohibitively expensive. We have built the working foundation, verified its architectural integrity, and established an empirical roadmap designed to answer our research questions rigorously. Thank you for your time and guidance. I welcome your questions and feedback."
