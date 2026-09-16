"""Small power/precision helpers for pilots."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ProportionCI:
    estimate: float
    lower: float
    upper: float


def wilson_ci(successes: int, total: int, *, z: float = 1.96) -> ProportionCI:
    if total <= 0:
        raise ValueError("total must be positive")
    phat = successes / total
    denom = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return ProportionCI(phat, max(0.0, centre - margin), min(1.0, centre + margin))


def candidate_ci_widths(rate: float, candidate_ns: list[int], *, z: float = 1.96) -> dict[int, float]:
    widths: dict[int, float] = {}
    for n in candidate_ns:
        ci = wilson_ci(round(rate * n), n, z=z)
        widths[n] = ci.upper - ci.lower
    return widths
