"""Evaluation metrics."""

from __future__ import annotations

from collections.abc import Iterable

from veritas.risk.calibrator import brier_score, negative_log_likelihood


def expected_calibration_error(probabilities: Iterable[float], labels: Iterable[int], *, bins: int = 10) -> float:
    pairs = list(zip(probabilities, labels))
    if not pairs:
        raise ValueError("cannot compute ECE with no examples")
    total = len(pairs)
    ece = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        bucket = [(p, y) for p, y in pairs if (lower <= p < upper) or (index == bins - 1 and p == 1.0)]
        if not bucket:
            continue
        confidence = sum(p for p, _ in bucket) / len(bucket)
        accuracy = sum(y for _, y in bucket) / len(bucket)
        ece += len(bucket) / total * abs(accuracy - confidence)
    return ece


def calibration_report(probabilities: Iterable[float], labels: Iterable[int], *, bins: int = 10) -> dict[str, float]:
    probs = list(probabilities)
    ys = list(labels)
    return {
        "brier": brier_score(probs, ys),
        "nll": negative_log_likelihood(probs, ys),
        "ece": expected_calibration_error(probs, ys, bins=bins),
    }
