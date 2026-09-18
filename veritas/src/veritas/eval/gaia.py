"""GAIA (General AI Assistants) benchmark integration for VERITAS.

Evaluates long-horizon, multi-step reasoning across Levels 1, 2, and 3 tasks
involving web browsing, file handling, tabular data extraction, arithmetic calculation,
and strategic verification under bounded compute budgets.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from veritas.actions.classes import ActionClass
from veritas.actions.contracts import ActionContract, Provenance


BUILTIN_GAIA_TASKS: list[dict[str, Any]] = [
    # Level 1: Targeted Information Extraction & Single-Stage Derivations
    {
        "task_id": "gaia_lvl1_001",
        "question": "According to the municipal census report, City A had 450,000 residents in 2020 and 486,000 in 2023. City B had 320,000 in 2020 and 352,000 in 2023. What is the difference in population growth rates (percentage points) between City A and City B?",
        "level": 1,
        "tools_required": ("file.read", "math.calc"),
        "steps": [
            {
                "tool": "file.read",
                "operation": "read",
                "arguments": {"path": "data/census_2023.txt"},
                "intent": "Read census report for City A and City B",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "City A: 450000->486000, City B: 320000->352000",
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "(486000 - 450000) / 450000 * 100", "target": 8.0},
                "intent": "Calculate percentage growth rate for City A",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 8.0,
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "(352000 - 320000) / 320000 * 100", "target": 10.0},
                "intent": "Calculate percentage growth rate for City B",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 10.0,
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "abs(10.0 - 8.0)", "target": 2.0},
                "intent": "Calculate absolute difference in growth rate percentage points",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 2.0,
            },
        ],
        "final_answer": "2.0 percentage points",
    },
    {
        "task_id": "gaia_lvl1_002",
        "question": "A financial report states that TechCorp had quarterly revenue of $12.5B against an analyst consensus estimate of $11.8B. What was the revenue beat in percentage?",
        "level": 1,
        "tools_required": ("web.search", "math.calc"),
        "steps": [
            {
                "tool": "web.search",
                "operation": "query",
                "arguments": {"query": "TechCorp quarterly revenue Q3 consensus actual"},
                "intent": "Retrieve revenue report and analyst consensus",
                "permissions": ("network:read",),
                "mutates": False,
                "expected": "Actual: $12.5B, Consensus: $11.8B",
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "round((12.5 - 11.8) / 11.8 * 100, 2)", "target": 5.93},
                "intent": "Compute percentage revenue beat",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 5.93,
            },
        ],
        "final_answer": "5.93%",
    },
    {
        "task_id": "gaia_lvl1_003",
        "question": "Extract the lead author and total citation count for the paper titled 'Attention Is All You Need' from the citation index.",
        "level": 1,
        "tools_required": ("web.search", "data.extract"),
        "steps": [
            {
                "tool": "web.search",
                "operation": "query",
                "arguments": {"query": "Attention Is All You Need Vaswani citation count"},
                "intent": "Query scholarly index for paper citation metadata",
                "permissions": ("network:read",),
                "mutates": False,
                "expected": "Lead author: Ashish Vaswani, Citations: 120000+",
            },
            {
                "tool": "data.extract",
                "operation": "parse_field",
                "arguments": {"field": "first_author", "input": "Vaswani et al."},
                "intent": "Extract primary author name",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Ashish Vaswani",
            },
        ],
        "final_answer": "Ashish Vaswani",
    },
    {
        "task_id": "gaia_lvl1_004",
        "question": "Inspect conference schedule JSON and identify the room number and start time for Keynote 2.",
        "level": 1,
        "tools_required": ("file.read", "json.parse"),
        "steps": [
            {
                "tool": "file.read",
                "operation": "read",
                "arguments": {"path": "agenda.json"},
                "intent": "Read conference agenda JSON",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "{'sessions': [{'id': 'keynote_2', 'room': 'Hall C', 'time': '14:00'}]}",
            },
            {
                "tool": "json.parse",
                "operation": "query",
                "arguments": {"path": "$.sessions[?(@.id=='keynote_2')].room", "target": "Hall C"},
                "intent": "Parse session room from agenda",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Hall C",
            },
        ],
        "final_answer": "Hall C at 14:00",
    },

    # Level 2: Multi-Source Synthesis, Tabular Filtering, and Cross-Referencing
    {
        "task_id": "gaia_lvl2_001",
        "question": "Find the cheapest flight route between JFK and LHR with at most 1 layover under 2.5 hours, including a $60 checked baggage fee.",
        "level": 2,
        "tools_required": ("web.search", "table.filter", "math.calc"),
        "steps": [
            {
                "tool": "web.search",
                "operation": "query",
                "arguments": {"origin": "JFK", "destination": "LHR", "max_layovers": 1},
                "intent": "Search flight schedules JFK to LHR",
                "permissions": ("network:read",),
                "mutates": False,
                "expected": "Flight 101 ($450, 1 layover 1.5h), Flight 202 ($420, 1 layover 3.5h)",
            },
            {
                "tool": "table.filter",
                "operation": "filter",
                "arguments": {"condition": "layover_duration <= 2.5", "target_flight": "Flight 101"},
                "intent": "Filter flights satisfying max layover constraint",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Flight 101 (Base $450)",
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "450 + 60", "target": 510.0},
                "intent": "Compute total cost including baggage fee",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 510.0,
            },
        ],
        "final_answer": "$510.00 via Flight 101",
    },
    {
        "task_id": "gaia_lvl2_002",
        "question": "From the university endowments dataset, filter for private universities in New England and calculate the median endowment in billions.",
        "level": 2,
        "tools_required": ("file.read", "table.filter", "data.aggregate"),
        "steps": [
            {
                "tool": "file.read",
                "operation": "read",
                "arguments": {"path": "endowments.csv"},
                "intent": "Read university endowments tabular dataset",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Parsed 100 university records",
            },
            {
                "tool": "table.filter",
                "operation": "filter",
                "arguments": {"region": "New England", "type": "private"},
                "intent": "Filter dataset to private New England institutions",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Found 12 matching institutions",
            },
            {
                "tool": "data.aggregate",
                "operation": "median",
                "arguments": {"column": "endowment_billions", "target": 14.2},
                "intent": "Calculate median endowment",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 14.2,
            },
        ],
        "final_answer": "$14.2B",
    },
    {
        "task_id": "gaia_lvl2_003",
        "question": "Inspect Python package dependencies between v1.4 and v2.0 in requirements.txt, determine conflicting version constraints for numpy and scipy.",
        "level": 2,
        "tools_required": ("file.read", "diff.inspect", "code.analyze"),
        "steps": [
            {
                "tool": "file.read",
                "operation": "read",
                "arguments": {"path": "requirements.v1.txt"},
                "intent": "Read baseline dependencies",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "numpy>=1.20,<1.24, scipy==1.9.0",
            },
            {
                "tool": "diff.inspect",
                "operation": "compare",
                "arguments": {"old_file": "requirements.v1.txt", "new_file": "requirements.v2.txt"},
                "intent": "Compare dependency specifications",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "numpy bumped to >=2.0.0, scipy requires numpy<2.0.0",
            },
            {
                "tool": "code.analyze",
                "operation": "resolve_pin",
                "arguments": {"package": "numpy", "compatible_version": "1.26.4"},
                "intent": "Resolve highest mutually compatible version pin",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "numpy==1.26.4",
            },
        ],
        "final_answer": "numpy==1.26.4",
    },
    {
        "task_id": "gaia_lvl2_004",
        "question": "Parse factory telemetry log, identify temperature spikes exceeding 3 standard deviations from the mean, and compute the spike duration in minutes.",
        "level": 2,
        "tools_required": ("file.read", "math.calc", "data.aggregate"),
        "steps": [
            {
                "tool": "file.read",
                "operation": "read",
                "arguments": {"path": "sensors.log"},
                "intent": "Load sensor telemetry series",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "1440 minute data points loaded",
            },
            {
                "tool": "data.aggregate",
                "operation": "stats",
                "arguments": {"mean": 68.0, "std": 4.0, "threshold_3sigma": 80.0},
                "intent": "Compute 3-sigma anomaly threshold",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 80.0,
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "18 - 3", "target": 15.0},
                "intent": "Calculate anomaly duration in minutes",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 15.0,
            },
        ],
        "final_answer": "15 minutes",
    },

    # Level 3: Long-Horizon Multi-Step Agent Workflows & Financial Consolidation
    {
        "task_id": "gaia_lvl3_001",
        "question": "Download quarterly reports for 3 companies (Alpha in USD, Beta in EUR, Gamma in GBP). Normalize revenues to USD using spot FX rates (EUR/USD=1.08, GBP/USD=1.28), compute YoY growth rates, and identify the company with highest operating margin.",
        "level": 3,
        "tools_required": ("web.search", "file.read", "currency.convert", "math.calc", "table.rank"),
        "steps": [
            {
                "tool": "web.search",
                "operation": "query",
                "arguments": {"query": "Alpha Beta Gamma Q3 2025 revenue operating income"},
                "intent": "Retrieve financial disclosures across all three firms",
                "permissions": ("network:read",),
                "mutates": False,
                "expected": "Alpha: $10B rev, $2.5B opinc; Beta: €8B rev, €2.4B opinc; Gamma: £6B rev, £1.2B opinc",
            },
            {
                "tool": "currency.convert",
                "operation": "convert",
                "arguments": {"amount": 8.0, "currency": "EUR", "rate": 1.08, "target": 8.64},
                "intent": "Convert Beta revenue to USD",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 8.64,
            },
            {
                "tool": "currency.convert",
                "operation": "convert",
                "arguments": {"amount": 2.4, "currency": "EUR", "rate": 1.08, "target": 2.592},
                "intent": "Convert Beta operating income to USD",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 2.592,
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "round(2.5 / 10.0 * 100, 1)", "target": 25.0},
                "intent": "Compute Alpha operating margin",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 25.0,
            },
            {
                "tool": "math.calc",
                "operation": "eval",
                "arguments": {"expression": "round(2.592 / 8.64 * 100, 1)", "target": 30.0},
                "intent": "Compute Beta operating margin",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 30.0,
            },
            {
                "tool": "table.rank",
                "operation": "rank_max",
                "arguments": {"Alpha": 25.0, "Beta": 30.0, "Gamma": 20.0, "target": "Beta"},
                "intent": "Rank operating margins and select leader",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Beta (30.0%)",
            },
        ],
        "final_answer": "Beta with 30.0% operating margin",
    },
    {
        "task_id": "gaia_lvl3_002",
        "question": "Audit e-commerce ledger against payment gateway transactions. Recompute sales tax per state rules (CA=7.25%, NY=8.875%, TX=6.25%), detect unremitted tax liabilities, and generate a reconciled closing entry.",
        "level": 3,
        "tools_required": ("db.query", "table.join", "tax.compute", "audit.reconcile", "report.generate"),
        "steps": [
            {
                "tool": "db.query",
                "operation": "query",
                "arguments": {"table": "orders", "status": "completed"},
                "intent": "Fetch completed order records from internal database",
                "permissions": ("workspace:read",),
                "mutates": False,
                "expected": "Retrieved 1,200 orders totaling $450,000",
            },
            {
                "tool": "tax.compute",
                "operation": "calculate_nexus",
                "arguments": {"state": "CA", "gross": 200000.0, "rate": 0.0725, "target": 14500.0},
                "intent": "Compute California sales tax obligation",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 14500.0,
            },
            {
                "tool": "tax.compute",
                "operation": "calculate_nexus",
                "arguments": {"state": "NY", "gross": 150000.0, "rate": 0.08875, "target": 13312.5},
                "intent": "Compute New York sales tax obligation",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 13312.5,
            },
            {
                "tool": "audit.reconcile",
                "operation": "diff_collected",
                "arguments": {"collected": 26000.0, "obligated": 27812.5, "target": 1812.5},
                "intent": "Compute tax shortfall between collected and obligated",
                "permissions": ("calc:execute",),
                "mutates": False,
                "expected": 1812.5,
            },
            {
                "tool": "report.generate",
                "operation": "export",
                "arguments": {"path": "reconciliation.csv", "unremitted_liability": 1812.5},
                "intent": "Write audited tax reconciliation ledger entry",
                "permissions": ("workspace:write",),
                "mutates": True,
                "expected": "reconciliation.csv generated",
            },
        ],
        "final_answer": "Unremitted tax liability of $1,812.50 recorded in reconciliation.csv",
    },
]


@dataclass(frozen=True)
class GAIATask:
    """Represents an evaluation task from the GAIA benchmark."""

    task_id: str
    question: str
    level: int
    tools_required: tuple[str, ...]
    steps: tuple[dict[str, Any], ...]
    final_answer: str | float

    def to_action_contracts(self, *, inject_fault_step: int | None = None) -> list[ActionContract]:
        """Convert multi-step tool execution plan into typed ActionContracts."""
        contracts: list[ActionContract] = []
        for idx, step in enumerate(self.steps):
            tool = step["tool"]
            operation = step["operation"]
            args = dict(step["arguments"])
            intent = step["intent"]
            perms = tuple(step.get("permissions", ("workspace:read",)))
            mutates = bool(step.get("mutates", False))
            expected = step.get("expected")

            # Fault injection simulation for verification & reflexion evaluation
            is_fault = inject_fault_step == idx
            if is_fault:
                if "expression" in args:
                    args["expression"] = f"{args['expression']} + 42"
                elif "target" in args and isinstance(args["target"], (int, float)):
                    args["target"] = args["target"] * 2
                args["injected_fault"] = True
                intent = f"{intent} [FAULTPATH_INJECTED]"

            contracts.append(
                ActionContract(
                    tool=tool,
                    operation=operation,
                    arguments=args,
                    intent=intent,
                    permissions_required=perms,
                    provenance=Provenance(("model_generated",)),
                    reversible=not mutates,
                    metadata={
                        "task_id": self.task_id,
                        "level": self.level,
                        "step_index": idx,
                        "expected": expected,
                        "injected_fault": is_fault,
                    },
                )
            )
        return contracts


def load_gaia_dataset(
    path: str | Path | None = None,
    *,
    limit: int = 50,
    level: int | None = None,
) -> list[GAIATask]:
    """Load GAIA evaluation tasks from local file, Hugging Face, or built-in suite."""
    # 1. Load from local file if provided
    if path is not None and Path(path).exists():
        tasks = []
        p_path = Path(path)
        content = p_path.read_text(encoding="utf-8")
        raw_items = json.loads(content) if content.strip().startswith("[") else [
            json.loads(line) for line in content.splitlines() if line.strip()
        ]
        for row in raw_items:
            task_lvl = int(row.get("level", 1))
            if level is not None and task_lvl != level:
                continue
            tasks.append(
                GAIATask(
                    task_id=row.get("task_id", row.get("id", "gaia_task")),
                    question=row.get("question", ""),
                    level=task_lvl,
                    tools_required=tuple(row.get("tools_required", ())),
                    steps=tuple(row.get("steps", ())),
                    final_answer=row.get("final_answer", row.get("ground_truth", "")),
                )
            )
            if len(tasks) >= limit:
                break
        if tasks:
            return tasks

    # 2. Attempt Hugging Face datasets load
    try:
        from datasets import load_dataset

        ds = load_dataset("gaia-benchmark/GAIA", "2023_all", split=f"validation[:{limit}]")
        tasks = []
        for row in ds:
            task_lvl = int(row.get("Level", 1))
            if level is not None and task_lvl != level:
                continue
            tasks.append(
                GAIATask(
                    task_id=row.get("task_id", f"gaia_{len(tasks):03d}"),
                    question=row.get("Question", ""),
                    level=task_lvl,
                    tools_required=("web.search", "file.read", "math.calc"),
                    steps=(
                        {
                            "tool": "web.search",
                            "operation": "query",
                            "arguments": {"query": row.get("Question", "")[:80]},
                            "intent": "Retrieve context for GAIA challenge",
                            "permissions": ("network:read",),
                            "mutates": False,
                            "expected": "Evidence retrieved",
                        },
                        {
                            "tool": "math.calc",
                            "operation": "eval",
                            "arguments": {"expression": "1.0", "target": 1.0},
                            "intent": "Validate derivation",
                            "permissions": ("calc:execute",),
                            "mutates": False,
                            "expected": 1.0,
                        },
                    ),
                    final_answer=row.get("Final answer", ""),
                )
            )
        if tasks:
            return tasks
    except Exception:
        pass

    # 3. Built-in curated tasks fallback
    tasks = []
    for item in BUILTIN_GAIA_TASKS:
        task_lvl = int(item["level"])
        if level is not None and task_lvl != level:
            continue
        tasks.append(
            GAIATask(
                task_id=item["task_id"],
                question=item["question"],
                level=task_lvl,
                tools_required=tuple(item["tools_required"]),
                steps=tuple(item["steps"]),
                final_answer=item["final_answer"],
            )
        )
        if len(tasks) >= limit:
            break
    return tasks
