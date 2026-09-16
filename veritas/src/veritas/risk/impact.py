"""Action impact scoring."""

from __future__ import annotations

from dataclasses import dataclass, field

from veritas.actions.contracts import ActionContract
from veritas.risk.features import ImpactFeatures


DEFAULT_WEIGHTS: dict[str, float] = {
    "mutation": 0.22,
    "irreversible": 0.20,
    "privilege": 0.14,
    "external": 0.16,
    "secret": 0.14,
    "untrusted": 0.08,
    "scope": 0.06,
}


def clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class ImpactScore:
    value: float
    features: ImpactFeatures
    weights: dict[str, float]


@dataclass(frozen=True)
class ImpactModel:
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))

    def score(self, contract: ActionContract) -> ImpactScore:
        features = ImpactFeatures.from_contract(contract)
        raw = sum(self.weights.get(name, 0.0) * value for name, value in features.to_dict().items())
        return ImpactScore(value=clip01(raw), features=features, weights=dict(self.weights))
