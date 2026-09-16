"""Calibration utilities for action-error probabilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


EPS = 1e-12


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def logit(probability: float) -> float:
    p = min(1.0 - EPS, max(EPS, probability))
    return math.log(p / (1.0 - p))


@dataclass(frozen=True)
class TemperatureCalibrator:
    temperature: float = 1.0
    input_is_probability: bool = False

    def calibrate(self, raw_score: float) -> float:
        score = logit(raw_score) if self.input_is_probability else raw_score
        return sigmoid(score / max(self.temperature, EPS))

    def calibrate_many(self, raw_scores: Iterable[float]) -> list[float]:
        return [self.calibrate(score) for score in raw_scores]

    @classmethod
    def fit(
        cls,
        raw_scores: Iterable[float],
        labels: Iterable[int],
        *,
        input_is_probability: bool = False,
        min_temperature: float = 0.25,
        max_temperature: float = 10.0,
        steps: int = 200,
    ) -> "TemperatureCalibrator":
        scores = list(raw_scores)
        ys = list(labels)
        if len(scores) != len(ys) or not scores:
            raise ValueError("raw_scores and labels must have the same non-zero length")

        best_t = 1.0
        best_nll = float("inf")
        for index in range(steps + 1):
            t = min_temperature + (max_temperature - min_temperature) * index / steps
            calibrator = cls(temperature=t, input_is_probability=input_is_probability)
            nll = negative_log_likelihood(calibrator.calibrate_many(scores), ys)
            if nll < best_nll:
                best_t = t
                best_nll = nll
        return cls(temperature=best_t, input_is_probability=input_is_probability)


def brier_score(probabilities: Iterable[float], labels: Iterable[int]) -> float:
    pairs = list(zip(probabilities, labels))
    if not pairs:
        raise ValueError("cannot compute Brier score with no examples")
    return sum((float(p) - int(y)) ** 2 for p, y in pairs) / len(pairs)


def negative_log_likelihood(probabilities: Iterable[float], labels: Iterable[int]) -> float:
    pairs = list(zip(probabilities, labels))
    if not pairs:
        raise ValueError("cannot compute NLL with no examples")
    total = 0.0
    for probability, label in pairs:
        p = min(1.0 - EPS, max(EPS, float(probability)))
        y = int(label)
        total -= y * math.log(p) + (1 - y) * math.log(1.0 - p)
    return total / len(pairs)
