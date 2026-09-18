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

## Frozen Hyperparameters and Empirical Statistics

### 1. Calibrator (Learned on held-out calibration set: 84 examples)
- **Method**: Temperature Scaling ($T > 0$)
- **Temperature ($T$)**: `10.0`
- **Expected Calibration Error (ECE)**: `0.0816` ($8.16\%$)
- **Brier Score**: `0.2484`
- **Negative Log-Likelihood (NLL)**: `0.6899`

### 2. Empirical Class-Level Verifier Characteristics
- `code_edit`: Detection Rate = 0.50, False Positive Rate = 0.00
- `destructive_filesystem`: Detection Rate = 1.00, False Positive Rate = 0.00
- `search`: Detection Rate = 1.00, False Positive Rate = 0.00
- `shell`: Detection Rate = 1.00, False Positive Rate = 0.00
- `test`: Detection Rate = 1.00, False Positive Rate = 0.00

### 3. Action Impact Feature Weights
- `mutation`: 0.22
- `irreversible`: 0.20
- `privilege`: 0.14
- `external`: 0.16
- `secret`: 0.14
- `untrusted`: 0.08
- `scope`: 0.06
- **Consequential Impact Threshold ($\tau_{\text{impact}}$)**: 0.50

### 4. Verification Budgets for Replay Sweeps
- Budgets ($B$): `[0.03, 0.06, 0.12, 0.24]`

### 5. Checkpoint & Cryptographic Invariance
- State hash invariance: $H(s_{\text{restored}}) = H(s_{\text{checkpoint}})$ verified with exact SHA-256 match.
- Residual damage after recovery: $\rho = 0.20$ (baseline) / empirical.

