# VERITAS: Thesis Pre-Defense Oral Script & Committee Q&A Guide

**Candidate:** Abidur Rahman Sadik  
**Thesis Title:** *VERITAS: Risk-Calibrated, Budget-Aware Verification and Counterfactual Recovery for State-Mutating LLM Agents*  
**Presentation Duration:** ~18 minutes (leaving 10–15 minutes for Committee Q&A)

---

## Part I: Slide-by-Slide Spoken Delivery & Timing

### Slide 1: Title & Candidacy Overview (Target Time: 0:00 – 1:00)
> **Spoken Delivery:**  
> "Respected members of the examination committee, supervisor, and colleagues: welcome to my thesis pre-defense. Today, I am presenting **VERITAS: Risk-Calibrated, Budget-Aware Verification and Counterfactual Recovery for State-Mutating LLM Agents**.  
> The goal of today’s pre-defense is twofold: first, to establish the mathematical formulation and architectural validity of resource-bounded verification, supported by our validated 72-module prototype; and second, to present the disciplined empirical campaign that I will execute between today’s pre-defense and the final defense."

---

### Slide 2: The Rise of State-Mutating Agents (Target Time: 1:00 – 2:15)
> **Spoken Delivery:**  
> "To understand why this research is necessary, we must look at how LLM agents are evolving. We are no longer dealing with simple conversational chatbots that produce ephemeral text. Today’s agents act directly inside software repositories, terminal environments, and cloud infrastructure.  
> The defining reality of tool-using agents is **action asymmetry**. When an agent runs `cat` or `grep`, the operation has deterministically zero side effects; verifying that step is a waste of compute. Conversely, when an agent executes a destructive bash command, edits critical business logic, or initiates a git push, an error has immediate, potentially irreversible consequences. Today’s agent systems either verify indiscriminately or don't verify at all because they treat all steps symmetrically."

---

### Slide 3: The Verification Dilemma & Failure of Extremes (Target Time: 2:15 – 3:30)
> **Spoken Delivery:**  
> "This observation exposes what we define as the **Verification Dilemma**.  
> On one extreme, we have 'Never Verify' agents—standard ReAct loops. They are fast and token-efficient, but brittle. A single silent error early in a 30-step trajectory will compound, leading to catastrophic failure.  
> On the other extreme, we have 'Always-Verify' reflective agents—like Reflexion or step-wise LLM critics. Verifying every single action balloons inference latency and token costs by three to ten times. Even worse, verifiers are not oracles—they make mistakes. If a verifier has a 10% false alarm rate, verifying 20 steps makes it mathematically probable that a perfectly valid run will be prematurely killed.  
> Therefore, verification compute is a **scarce, expensive resource**. The core scientific question is: *Given a bounded compute budget, WHICH actions should an agent verify before execution?*"

---

### Slide 4: Research Questions & Hypotheses (Target Time: 3:30 – 4:45)
> **Spoken Delivery:**  
> "To address this challenge, our thesis is framed around four specific, falsifiable research questions:  
> - **Primary RQ:** Under a fixed compute budget, can a risk-calibrated value-of-verification controller catch more consequential errors than simpler uncertainty-only or product-based policies?  
> - **RQ1 on Calibration:** Can step-level action error probabilities be reliably calibrated in multi-turn agent environments?  
> - **RQ2 on Budget Allocation:** Does selective gating catch more consequential errors per unit compute than uniform or random spend?  
> - **RQ3 on Falsifiability:** Does full RC-VoV beat the simple product baseline $p_e \times I$? This is our pre-registered stop rule. If it does not, we simplify our method.  
> - **RQ4 on Recovery:** Does transactional checkpoint rollback reduce residual task loss $\rho_t$ compared to cold restarts?"

---

### Slide 5: Positioning in Prior Art (Target Time: 4:45 – 6:00)
> **Spoken Delivery:**  
> "VERITAS sits at the convergence of three major research streams:  
> 1. *Reflective agents*, such as Reflexion and ReVISE, which introduce self-correction but lack action impact modeling and ignore compute budgets.  
> 2. *Agent security guardrails*, like GuardAgent and AgentDojo, which provide safety filtering but treat tools symmetrically and terminate runs rather than recovering state.  
> 3. *Budget-aware inference*, such as BAVAR, which formulates resource trade-offs but assumes synthetic error rates and lacks execution recovery.  
> VERITAS unifies these disjoint areas into a decision-theoretic control runtime that pairs calibrated error probability, multidimensional action impact, empirical verifier operating characteristics, and rollback recovery under a strict budget."

---

### Slide 6: End-to-End System Architecture (Target Time: 6:00 – 7:30)
> **Spoken Delivery:**  
> "This brings us to the **end-to-end architecture** of VERITAS. The runtime operates across seven structured stages:  
> 1. A competent policy model proposes a candidate action.  
> 2. The action contract and permission boundary deterministically validate schemas, path traversal safety, and operational permissions.  
> 3. The risk and calibration engine estimates the calibrated error probability $p_e$ and calculates the multidimensional impact score $I_t$.  
> 4. The RC-VoV budget controller calculates the expected net benefit $\Delta_t$ and checks if marginal utility meets the adaptive budget threshold.  
> 5. If verification is triggered, deterministic checks and semantic falsification probes run.  
> 6. State-mutating actions trigger a transactional workspace snapshot before execution in the isolated sandbox, enabling instant rollback if falsified or broken.  
> 7. All decisions, features, and costs are permanently logged to JSONL for offline matched-budget replay."

---

### Slide 7: Action Contracts & Impact Vector (Target Time: 7:30 – 8:45)
> **Spoken Delivery:**  
> "Looking deeper into Stage 2 and 3: in ordinary agents, tools are invoked as unstructured strings passed to a bash subprocess. In VERITAS, every tool invocation is an `ActionContract`. It explicitly declares its action class, mutation status, irreversibility, and preconditions.  
> Action impact $I_t$ is computed across seven normalized dimensions: whether it mutates state, irreversibility, privilege level, external blast radius, secret exposure, untrusted data provenance, and blast scope. Furthermore, hard-critical operations—such as recursive deletion or force-pushing commits—trigger an immediate deterministic verification override regardless of model confidence."

---

### Slide 8: Mathematical Core - RC-VoV Formulation (Target Time: 8:45 – 10:15)
> **Spoken Delivery:**  
> "Slide 8 is the mathematical foundation of our thesis. We formulate verification as a decision-theoretic optimization problem.  
> If we skip verification, our expected loss is simply $p_{e,t} I_t$.  
> If we verify, our expected loss comprises the direct verification compute cost $C_{v,t}$, the residual loss of missed errors plus recovered errors, and the false alarm penalty.  
> Subtracting the two gives the expected value of verification, $\Delta_t$:  
> $$\Delta_t = p_{e,t} d_t (1 - \rho_t) I_t - C_{v,t} - (1 - p_{e,t}) f_t C_{fp,t}$$  
> Notice the elegant properties of this equation:  
> - If recovery is impossible—meaning $\rho_t = 1$—the avoided loss term collapses to zero! Why spend compute verifying an unrecoverable action if verification cannot mitigate the loss?  
> - If the verifier is noisy—meaning $f_t$ is high—the third penalty term dominates and suppresses verification.  
> Verification is only executed when $\Delta_t > 0$ and marginal utility justifies the budget."

---

### Slide 9: Dynamic Budget Controller & Baselines (Target Time: 10:15 – 11:30)
> **Spoken Delivery:**  
> "To enforce a hard compute budget, we compute marginal utility per verification dollar. As the budget burns down, our controller escalates the hurdle rate $\lambda_t$.  
> Crucially, we introduce the **mandatory simple-product baseline**: $v_t = \mathbf{1}[p_{e,t} I_t > \tau]$.  
> Why is this mandatory? Because if verifier sensitivity, false alarm rates, and recovery are roughly constant across actions, the RC-VoV equation naturally reduces to error probability times impact. If our full mathematical formulation cannot beat this simple product under equal compute, the additional terms do not justify their empirical cost."

---

### Slide 10: Checkpoint & Recovery Architecture (Target Time: 11:30 – 12:45)
> **Spoken Delivery:**  
> "Slide 10 details our checkpoint and recovery engine. In standard agent frameworks, when an action fails or introduces a fatal bug, the agent either wanders into hallucinated loops or restarts from step zero, destroying 20 steps of prior compute.  
> In VERITAS, whenever a state-mutating action is scheduled, the runtime takes a lightweight workspace snapshot authenticated by SHA-256 hashes. If the action is falsified or fails execution, the sandbox performs an atomic rollback to the pre-action snapshot in milliseconds. The policy is then prompted with counterfactual feedback to branch an alternative action, preserving prior reasoning and drastically reducing residual loss $\rho_t$."

---

### Slide 11: Work Completed So Far - Prototype (Target Time: 12:45 – 13:45)
> **Spoken Delivery:**  
> "I want to emphasize that VERITAS is not merely an architectural diagram—it is a working, tested research prototype.  
> The codebase comprises 72 Python modules across actions, risk, recovery, verification, and evaluation. Our test suite passes all 21 unit and integration tests, as well as 10,000 property-based randomized invariant checks verifying that our mathematical equations behave strictly within theoretical bounds under arbitrary inputs. We have also verified SHA-256 tamper detection and path traversal rejections."

---

### Slide 12: Offline Replay Architecture (Target Time: 13:45 – 14:45)
> **Spoken Delivery:**  
> "Slide 12 solves the financial and compute bottleneck of agent research. Evaluating 10 schedulers across hundreds of SWE-bench tasks online would cost thousands of dollars and weeks of GPU compute.  
> Instead, we perform a single expensive logging pass with a frontier model, recording rich action traces. We then feed these exact identical logged decisions into our offline replay engine across different budget tiers. This allows us to plot clean, controlled allocation efficiency curves across all baselines with zero policy variance."

---

### Slide 13 – 17: What I Am Going to Do (Empirical Campaign) (Target Time: 14:45 – 17:00)
> **Spoken Delivery:**  
> "Now, let us examine the core of this pre-defense: **What I am going to do** between today and the final defense:  
> - **In Phase 1 & 2:** We complete our local RTX 5080 vLLM inference stack, enforcing an operational safety cap of 90% peak VRAM, and finalize our hardened Docker sandbox with zero network access. We then log trajectories from 150 tasks in SWE-bench Verified. Crucially, we enforce non-circular ground truth labeling.  
> - **In Phase 3:** We perform empirical calibration. We fit temperature scaling on a held-out calibration split of over 300 actions, and we compute class-level verifier sensitivity $d$, false alarm rate $f$, and recovery loss $\rho$ from real trials.  
> - **In Phase 4:** We execute our matched-budget replay sweep across budgets from 0% to 100%. We measure consequential errors caught per compute token, and we enforce our pre-registered stop rule.  
> - **In Phase 5:** We execute our controlled recovery experiment comparing rollback against cold restarts, and we run a 30-task pilot for statistical power analysis before deploying the Top-3 schedulers for final online benchmark evaluation."

---

### Slide 18 – 20: Timeline, Risk Mitigation & Conclusion (Target Time: 17:00 – 18:00)
> **Spoken Delivery:**  
> "Our timeline targets final thesis completion by February 2027. We have explicitly mitigated research risks: if $p_e \times I$ matches RC-VoV, we will publish it honestly as a scientific finding on the primacy of impact and uncertainty. Local GPU memory is protected by strict VRAM margins and AWQ quantization.  
> In summary, VERITAS provides a principled, falsifiable framework for making autonomous agents reliable without making them prohibitively expensive. We have validated the core prototype, and our empirical roadmap is pre-registered and ready for execution.  
> Thank you for your time and guidance. I welcome your questions and feedback."

---

## Part II: 10 Tough Committee Questions & Winning Defenses

### Q1: "Why not just use a more capable model (e.g., GPT-5 or Claude 3.5 Sonnet) and skip building a complex verifier?"
> **Winning Defense:**  
> "Even frontier models have non-zero failure rates on long-horizon tasks—SWE-bench Verified resolution rates for top models currently plateau between 35% and 50%. More importantly, increasing model size increases per-token inference cost quadratically without solving action asymmetry. A trillion-parameter model can still hallucinate a destructive bash command or an invalid syntax patch. VERITAS provides an external, model-agnostic control envelope with deterministic contracts and checkpoint recovery that operates regardless of the underlying policy model."

### Q2: "What if the simple baseline $p_{e,t} I_t$ beats or matches your full RC-VoV formulation? Does that invalidate your thesis?"
> **Winning Defense:**  
> "Not at all—in fact, that would be an impactful scientific result. In literature, authors often introduce complex multi-term equations without proving that the added terms provide empirical value over simpler baselines. We have explicitly pre-registered this as our stop rule. If $p_e \times I$ matches RC-VoV, it proves that in practical agent environments, action impact and calibrated uncertainty dominate higher-order verifier noise. We would simplify the runtime, document why the additional parameters collapsed, and publish it as an honest, falsifiable contribution."

### Q3: "How do you prevent circularity when determining ground truth action errors?"
> **Winning Defense:**  
> "Circularity is a major threat in agent evaluation—if the verifier's opinion or the tool's return code is used as ground truth, the evaluation is rigged. In VERITAS, ground truth error labels ($Y_t \in \{0, 1\}$) are determined independently through SWE-bench unit test suites and dual-annotator manual adjudication on discordant traces. A tool return code of 0 does not mean the action was correct; conversely, a verifier rejection does not mean the action was flawed. Ground truth is isolated from runtime verifier outputs."

### Q4: "Why use a local 7B verifier on an RTX 5080 instead of calling frontier APIs for verification?"
> **Winning Defense:**  
> "Three reasons: first, **latency**—running local tensor-parallel inference on the RTX 5080 provides sub-100ms verification checks, whereas external API roundtrips introduce multi-second network and queuing delays. Second, **cost**—calling commercial APIs for verification at every decision point would make large-scale deployment economically unviable. Third, **reproducibility**—local models provide fixed weights and determinism, ensuring that thesis experiments can be audited and reproduced by any research lab without proprietary model drift."

### Q5: "How is the action impact vector $I_t$ computed? Isn't assigning weights $w$ subjective?"
> **Winning Defense:**  
> "The impact vector is based on objective, deterministic attributes: Does the action mutate state? Is it reversible? Does it require elevated permissions? Does it touch secrets or network endpoints? In Paper 1, we use transparent expert-defined weights and report them openly. More importantly, we conduct a sensitivity ablation across weight variations to prove that our results are robust to weight tuning rather than overfitted to a specific vector."

### Q6: "Why not use sequential e-values or formal statistical hypothesis tests for every action?"
> **Winning Defense:**  
> "A sequential e-value process requires valid probability spaces and well-defined null hypotheses where $\mathbb{E}_{H_0}[e_i] \le 1$. In software engineering and tool use, an LLM outputting `[PASS]` or `[FAIL]` is a heuristic classifier, not a statistical experiment. Claiming that an LLM critic generates a formal e-value is scientifically unsound. In VERITAS, we call it what it is: a calibrated evidence score or falsification verdict, preserving mathematical honesty."

### Q7: "How does checkpointing scale on large codebases? Won't taking snapshots cause severe disk I/O bottlenecks?"
> **Winning Defense:**  
> "VERITAS only snapshots when an action mutates persistent state (`action.mutates_state = True`). Furthermore, because we run inside a localized workspace, our snapshot engine uses copy-on-write directory links and tracking of modified file diffs rather than duplicating the entire disk image. In our benchmarks, snapshot creation takes less than 25 milliseconds and workspace state hashing takes under 5 milliseconds, creating virtually unnoticeable overhead."

### Q8: "What is the computational overhead of running temperature calibration and RC-VoV dynamically?"
> **Winning Defense:**  
> "The mathematical evaluation of temperature scaling, impact clipping, and the RC-VoV equation takes less than 0.1 milliseconds on a single CPU core. In our invariant tests, 10,000 evaluations completed in under 80 milliseconds. The computational cost of the controller itself is virtually zero compared to the hundreds of milliseconds spent generating LLM tokens."

### Q9: "Why focus primarily on SWE-bench Verified instead of benchmarks like GAIA or AgentBench?"
> **Winning Defense:**  
> "SWE-bench Verified provides deterministic ground truth (pre-existing unit tests written by human maintainers), rich state mutation (editing Python files, installing libraries, modifying configs), and complex multi-turn horizons (averaging 15–40 actions per task). GAIA and web benchmarks suffer from web endpoint instability and brittle DOM changes. SWE-bench Verified provides the gold-standard testbed for state-mutating tool verification."

### Q10: "What happens if an error occurs on an irreversible action that cannot be rolled back?"
> **Winning Defense:**  
> "That is precisely why the RC-VoV equation incorporates $\rho_t$ and the hard-critical override. For irreversible actions (e.g., dropping a database or external webhooks), the rollback residual loss $\rho_t = 1.0$, which means recovery is impossible. In that case, our architecture triggers a **hard-critical deterministic gate**: the action cannot bypass verification based on model confidence alone, and if verified false, execution is blocked before the irreversible mutation occurs."
