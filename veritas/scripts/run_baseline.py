"""Run baseline schedulers on a tiny built-in action dataset."""

from __future__ import annotations

import json

from veritas.eval.baselines import default_schedulers
from veritas.eval.replay import ReplayEngine


def demo_records() -> tuple[dict, ...]:
    return (
        {
            "action_id": "act_read",
            "action_class": "read",
            "calibrated_error_probability": 0.1,
            "impact": 0.05,
            "detection_rate_estimate": 0.6,
            "false_positive_rate_estimate": 0.05,
            "residual_loss_after_recovery": 0.4,
            "estimated_cost": 0.03,
            "ground_truth_label": "correct",
            "verifier_verdict": "pass",
        },
        {
            "action_id": "act_bad_edit",
            "action_class": "code_edit",
            "calibrated_error_probability": 0.7,
            "impact": 0.62,
            "detection_rate_estimate": 0.8,
            "false_positive_rate_estimate": 0.08,
            "residual_loss_after_recovery": 0.2,
            "estimated_cost": 0.03,
            "ground_truth_label": "error",
            "verifier_verdict": "fail",
        },
    )


def main() -> None:
    engine = ReplayEngine(demo_records())
    results = engine.sweep(default_schedulers(), budgets=[0.03, 0.06])
    print(json.dumps([result.to_dict() for result in results], indent=2))


if __name__ == "__main__":
    main()
