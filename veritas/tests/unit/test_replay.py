import unittest

from veritas.eval.baselines import ErrorImpactScheduler, NeverScheduler, RandomBudgetMatchedScheduler
from veritas.eval.replay import ReplayEngine


def records() -> tuple[dict, ...]:
    return (
        {
            "action_id": "a1",
            "action_class": "read",
            "calibrated_error_probability": 0.1,
            "impact": 0.1,
            "estimated_cost": 0.03,
            "ground_truth_label": "correct",
            "verifier_verdict": "pass",
        },
        {
            "action_id": "a2",
            "action_class": "code_edit",
            "calibrated_error_probability": 0.8,
            "impact": 0.8,
            "estimated_cost": 0.03,
            "ground_truth_label": "error",
            "verifier_verdict": "fail",
        },
    )


class ReplayTests(unittest.TestCase):
    def test_error_impact_replay_catches_consequential_error(self) -> None:
        result = ReplayEngine(records()).run(ErrorImpactScheduler(threshold=0.25), budget=0.03)

        self.assertEqual(result.selected_action_ids, ("a2",))
        self.assertEqual(result.consequential_errors_caught, 1)

    def test_never_replay_selects_nothing(self) -> None:
        result = ReplayEngine(records()).run(NeverScheduler(), budget=1.0)

        self.assertEqual(result.selected_count, 0)
        self.assertEqual(result.verification_cost, 0)

    def test_random_baseline_is_reproducible_across_repeated_runs(self) -> None:
        scheduler = RandomBudgetMatchedScheduler(seed=17)
        engine = ReplayEngine(records())

        first = engine.run(scheduler, budget=1.0)
        second = engine.run(scheduler, budget=1.0)

        self.assertEqual(first.selected_action_ids, second.selected_action_ids)

    def test_random_baseline_fills_available_budget(self) -> None:
        result = ReplayEngine(records()).run(RandomBudgetMatchedScheduler(seed=3), budget=0.06)

        self.assertEqual(result.selected_count, 2)
        self.assertAlmostEqual(result.verification_cost, 0.06)
