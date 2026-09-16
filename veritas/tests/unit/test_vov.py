import unittest

from veritas.risk.vov import BudgetController, VovInputs, compute_vov


class VovTests(unittest.TestCase):
    def test_vov_increases_with_impact(self) -> None:
        low = compute_vov(
            VovInputs(
                p_error=0.6,
                impact=0.2,
                detection_rate=0.8,
                false_positive_rate=0.05,
                residual_loss_after_recovery=0.2,
                verification_cost=0.01,
            )
        )
        high = compute_vov(
            VovInputs(
                p_error=0.6,
                impact=0.8,
                detection_rate=0.8,
                false_positive_rate=0.05,
                residual_loss_after_recovery=0.2,
                verification_cost=0.01,
            )
        )

        self.assertGreater(high.delta, low.delta)

    def test_budget_controller_respects_insufficient_budget(self) -> None:
        vov = compute_vov(
            VovInputs(
                p_error=0.9,
                impact=0.9,
                detection_rate=0.9,
                false_positive_rate=0.0,
                residual_loss_after_recovery=0.0,
                verification_cost=0.5,
            )
        )
        decision = BudgetController().choose(vov, cost=0.5, remaining=0.1, total=1.0)

        self.assertFalse(decision.selected)
        self.assertEqual(decision.reason, "insufficient_budget")

    def test_hard_critical_action_does_not_overdraw_budget(self) -> None:
        vov = compute_vov(
            VovInputs(
                p_error=0.9,
                impact=1.0,
                detection_rate=0.9,
                false_positive_rate=0.0,
                residual_loss_after_recovery=0.0,
                verification_cost=0.5,
            )
        )

        decision = BudgetController().choose(
            vov, cost=0.5, remaining=0.1, total=1.0, hard_critical=True
        )

        self.assertFalse(decision.selected)
        self.assertEqual(decision.reason, "insufficient_budget")
