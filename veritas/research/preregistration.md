# VERITAS Paper 1 Preregistration

## Primary Question

Under a fixed verification budget, does RC-VoV catch more consequential state-mutating action errors than simpler gates, especially calibrated error probability x action impact?

## Mandatory Baselines

- never verify
- always verify
- confidence threshold
- risk-only
- error x impact
- mutation-only
- random budget-matched
- BAVAR-style expected value
- RC-VoV without recovery
- RC-VoV with class-level verifier and recovery statistics

## Stop Rule

If RC-VoV does not beat error x impact on held-out matched-budget replay, simplify the controller before scaling online evaluation.

## Leakage Rule

Thresholds, calibrators, impact weights, verifier statistics, and recovery statistics must be frozen before final test evaluation.
