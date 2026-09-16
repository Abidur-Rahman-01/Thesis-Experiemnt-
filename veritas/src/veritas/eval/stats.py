"""General statistics helpers."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence


def bootstrap_ci(
    values: Sequence[float],
    *,
    statistic: Callable[[Sequence[float]], float] | None = None,
    samples: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:
    if not values:
        raise ValueError("values must be non-empty")
    stat = statistic or (lambda xs: sum(xs) / len(xs))
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        draw = [rng.choice(values) for _ in values]
        estimates.append(stat(draw))
    estimates.sort()
    lower = estimates[int((alpha / 2) * samples)]
    upper = estimates[min(samples - 1, int((1 - alpha / 2) * samples))]
    return lower, upper
