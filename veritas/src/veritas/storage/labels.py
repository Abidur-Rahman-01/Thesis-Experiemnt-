"""Action labels kept separate from predictor outputs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionLabel:
    action_id: str
    label: str
    label_source: str
    evidence_ref: str | None = None
    adjudication_status: str = "accepted"

    def to_dict(self) -> dict[str, str | None]:
        return {
            "action_id": self.action_id,
            "label": self.label,
            "label_source": self.label_source,
            "evidence_ref": self.evidence_ref,
            "adjudication_status": self.adjudication_status,
        }
