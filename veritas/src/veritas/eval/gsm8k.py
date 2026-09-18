"""GSM8K (Grade School Math 8K) reasoning benchmark integration for VERITAS.

Converts multi-step reasoning and arithmetic problems into action contract sequences,
evaluating strategic verification, POPPER invariant falsification, Reflexion recovery,
and CSO preference harvesting.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from veritas.actions.classes import ActionClass
from veritas.actions.contracts import ActionContract, Provenance


# Representative sample of public GSM8K problems for instant offline benchmarking
BUILTIN_GSM8K_SAMPLE = [
    {
        "id": "gsm8k_001",
        "question": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
        "steps": [
            {"expr": "48 / 2", "expected": 24.0, "intent": "Calculate clips sold in May"},
            {"expr": "48 + 24", "expected": 72.0, "intent": "Calculate total clips sold in April and May"},
        ],
        "final_answer": 72.0,
    },
    {
        "id": "gsm8k_002",
        "question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
        "steps": [
            {"expr": "50 / 60", "expected": 0.8333333333333334, "intent": "Convert 50 minutes to fraction of an hour"},
            {"expr": "12 * (50 / 60)", "expected": 10.0, "intent": "Calculate earnings for 50 minutes at $12/hr"},
        ],
        "final_answer": 10.0,
    },
    {
        "id": "gsm8k_003",
        "question": "Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents gave her twice as much as her parents. How much more money does Betty need to buy the wallet?",
        "steps": [
            {"expr": "100 / 2", "expected": 50.0, "intent": "Calculate money Betty currently has"},
            {"expr": "15 * 2", "expected": 30.0, "intent": "Calculate gift from grandparents"},
            {"expr": "50 + 15 + 30", "expected": 95.0, "intent": "Calculate total money collected so far"},
            {"expr": "100 - 95", "expected": 5.0, "intent": "Calculate remaining money needed"},
        ],
        "final_answer": 5.0,
    },
    {
        "id": "gsm8k_004",
        "question": "A deep-sea monster rises from the waters once every 100 years to feast on a ship and then returns to sleep. In 837 years, how many ships has it feasted on?",
        "steps": [
            {"expr": "837 // 100", "expected": 8.0, "intent": "Calculate complete 100-year periods in 837 years"},
        ],
        "final_answer": 8.0,
    },
    {
        "id": "gsm8k_005",
        "question": "Mark has a garden with flowers. He has 10 rows with 15 yellow flowers and 5 rows with 20 red flowers. How many flowers does he have in total?",
        "steps": [
            {"expr": "10 * 15", "expected": 150.0, "intent": "Calculate total yellow flowers"},
            {"expr": "5 * 20", "expected": 100.0, "intent": "Calculate total red flowers"},
            {"expr": "150 + 100", "expected": 250.0, "intent": "Calculate grand total flowers"},
        ],
        "final_answer": 250.0,
    },
]


@dataclass(frozen=True)
class GSM8KProblem:
    problem_id: str
    question: str
    steps: tuple[dict[str, Any], ...]
    final_answer: float

    def to_action_contracts(self, *, inject_fault_step: int | None = None) -> list[ActionContract]:
        """Convert multi-step reasoning solution into typed action contracts."""
        contracts = []
        for idx, step in enumerate(self.steps):
            expr = step["expr"]
            intent = step["intent"]
            expected = step["expected"]

            # Optionally simulate realistic agent calculation error at a specific step
            if inject_fault_step == idx:
                faulty_expr = f"{expr} + 10"  # Hallucinated addition error
                contracts.append(
                    ActionContract(
                        tool="math.calc",
                        operation="eval",
                        arguments={"expression": faulty_expr, "target": expected, "injected_fault": True},
                        intent=f"{intent} [faulty]",
                        permissions_required=("calc:execute",),
                        provenance=Provenance(("model_generated",)),
                        reversible=True,
                        metadata={"problem_id": self.problem_id, "step_index": idx, "expected": expected},
                    )
                )
            else:
                contracts.append(
                    ActionContract(
                        tool="math.calc",
                        operation="eval",
                        arguments={"expression": expr, "target": expected},
                        intent=intent,
                        permissions_required=("calc:execute",),
                        provenance=Provenance(("model_generated",)),
                        reversible=True,
                        metadata={"problem_id": self.problem_id, "step_index": idx, "expected": expected},
                    )
                )
        return contracts


def load_gsm8k_dataset(
    path: str | Path | None = None,
    *,
    limit: int = 50,
    split: str = "test",
) -> list[GSM8KProblem]:
    """Load GSM8K problems from Hugging Face dataset, JSON/JSONL file, or built-in sample."""
    # 1. If explicit local file is given and exists, load from file
    if path is not None and Path(path).exists():
        problems = []
        p_path = Path(path)
        lines = p_path.read_text(encoding="utf-8").splitlines()
        for line_idx, line in enumerate(lines[:limit]):
            if not line.strip():
                continue
            row = json.loads(line)
            q = row.get("question", "")
            ans_text = row.get("answer", "")
            raw_steps = re.findall(r"<<(.*?)=(.*?)>>", ans_text)
            match = re.search(r"####\s*(-?[\d\.,]+)", ans_text)
            final_val = float(match.group(1).replace(",", "")) if match else 0.0

            steps = [
                {"expr": expr.strip(), "expected": float(val.replace(",", "").strip()), "intent": f"Reasoning step: {expr}"}
                for expr, val in raw_steps
                if val.replace(",", "").strip().replace(".", "", 1).replace("-", "", 1).isdigit()
            ]
            if not steps:
                steps = [{"expr": "calc", "expected": final_val, "intent": "Derive answer"}]

            problems.append(
                GSM8KProblem(
                    problem_id=row.get("id", f"gsm8k_{line_idx:04d}"),
                    question=q,
                    steps=tuple(steps),
                    final_answer=final_val,
                )
            )
        return problems

    # 2. Try loading from Hugging Face datasets
    try:
        from datasets import load_dataset

        ds = load_dataset("openai/gsm8k", "main", split=f"{split}[:{limit}]")
        problems = []
        for line_idx, row in enumerate(ds):
            q = row["question"]
            ans_text = row["answer"]
            raw_steps = re.findall(r"<<(.*?)=(.*?)>>", ans_text)
            match = re.search(r"####\s*(-?[\d\.,]+)", ans_text)
            final_val = float(match.group(1).replace(",", "")) if match else 0.0

            steps = []
            for expr, val in raw_steps:
                clean_val = val.replace(",", "").strip()
                try:
                    expected_num = float(clean_val)
                    steps.append({"expr": expr.strip(), "expected": expected_num, "intent": f"Reasoning step: {expr}"})
                except ValueError:
                    continue

            if not steps:
                steps = [{"expr": "calc", "expected": final_val, "intent": "Derive final answer"}]

            problems.append(
                GSM8KProblem(
                    problem_id=f"gsm8k_{split}_{line_idx:04d}",
                    question=q,
                    steps=tuple(steps),
                    final_answer=final_val,
                )
            )
        if problems:
            return problems
    except Exception:
        pass

    # 3. Built-in sample fallback
    return [
        GSM8KProblem(
            problem_id=p["id"],
            question=p["question"],
            steps=tuple(p["steps"]),
            final_answer=p["final_answer"],
        )
        for p in BUILTIN_GSM8K_SAMPLE
    ]
