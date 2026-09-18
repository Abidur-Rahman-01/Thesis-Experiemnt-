"""Score and enrich raw action logs with impact, error probability, and verifier verdicts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from veritas.actions.contracts import ActionContract
from veritas.actions.permissions import PermissionPolicy
from veritas.core.orchestrator import _hard_critical
from veritas.models.base import PolicyContext
from veritas.models.local import HeuristicErrorEstimator
from veritas.risk.calibrator import TemperatureCalibrator
from veritas.risk.impact import ImpactModel
from veritas.storage.events import JSONLEventStore
from veritas.verification.action_falsifier import ActionFalsifier
from veritas.verification.deterministic import DeterministicVerifier


def score_record(record: dict, impact_model: ImpactModel, estimator: HeuristicErrorEstimator, falsifier: ActionFalsifier, calibrator: TemperatureCalibrator) -> dict:
    row = dict(record)
    contract_data = row.get("action_json")
    if not contract_data:
        return row

    contract = ActionContract.from_mapping(contract_data)
    impact_score = impact_model.score(contract)
    row["impact"] = impact_score.value

    context = PolicyContext(goal=str(row.get("task_id", "")), history=(), step_index=int(row.get("step", 0)))
    err_estimate = estimator.estimate(context, contract)
    row["raw_error_score"] = err_estimate.raw_score
    row["calibrated_error_probability"] = calibrator.calibrate(err_estimate.raw_score)

    verification = falsifier.verify(contract)
    if verification.verdict == "fail" or row.get("execution_success") is False:
        row["verifier_verdict"] = "fail"
    else:
        row["verifier_verdict"] = "pass"
    row["verification_cost"] = verification.cost
    row["hard_critical"] = _hard_critical(contract.action_class.value, contract.operation)

    # Assign deterministic evidence labels for offline replay
    is_success = row.get("execution_success")
    if is_success is False:
        row["ground_truth_label"] = "error"
        row["label_source"] = "execution_failure"
    elif is_success is True:
        row["ground_truth_label"] = "correct"
        row["label_source"] = "execution_success"
    else:
        row["ground_truth_label"] = "unresolved"
        row["label_source"] = "unlabeled"

    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich action records with impact, error scores, and verifier verdicts")
    parser.add_argument("input", type=Path, help="Input raw JSONL action log")
    parser.add_argument("output", type=Path, help="Output enriched JSONL action log")
    args = parser.parse_args()

    permissions = PermissionPolicy(
        granted_permissions=frozenset({"workspace:read", "workspace:write"}),
        allowed_tools=frozenset({"shell.exec", "fs"}),
    )
    impact_model = ImpactModel()
    estimator = HeuristicErrorEstimator(impact_model=impact_model)
    falsifier = ActionFalsifier(DeterministicVerifier(permissions))
    calibrator = TemperatureCalibrator(temperature=1.0)

    store = JSONLEventStore(args.input)
    raw_records = store.read_all()
    scored_records = [score_record(r, impact_model, estimator, falsifier, calibrator) for r in raw_records]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for r in scored_records:
            handle.write(json.dumps(r, sort_keys=True) + "\n")

    print(f"scored and enriched {len(scored_records)} records -> {args.output}")


if __name__ == "__main__":
    main()
