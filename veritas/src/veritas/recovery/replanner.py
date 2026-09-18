"""Counterfactual replanning interfaces incorporating Reflexion and SE-Agent loops."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable

from veritas.actions.contracts import ActionContract


@dataclass(frozen=True)
class ReplanCandidate:
    action: ActionContract
    score: float
    rationale: str


class NoopReplanner:
    def propose(self, failed_action: ActionContract, *, reason: str = "") -> list[ReplanCandidate]:
        return []


@dataclass
class ReflexionReplanner:
    """Proposes alternative actions using error reflection and counterfactual exploration."""

    generator: Callable[[str], str] | None = None
    max_candidates: int = 3

    def build_reflection_prompt(self, failed_action: ActionContract, reason: str, goal: str = "") -> str:
        return (
            f"[Reflexion Feedback]\n"
            f"Goal: {goal or failed_action.intent}\n"
            f"Failed Action: {failed_action.tool}.{failed_action.operation}\n"
            f"Arguments: {failed_action.arguments}\n"
            f"Verification / Execution Error: {reason}\n"
            f"Instructions: Identify the cause of the failure and formulate an alternative, non-destructive action."
        )

    def propose(
        self,
        failed_action: ActionContract,
        *,
        reason: str = "Action failed verification or execution",
        goal: str = "",
    ) -> list[ReplanCandidate]:
        reflection = self.build_reflection_prompt(failed_action, reason, goal)
        candidates: list[ReplanCandidate] = []

        if self.generator is not None:
            try:
                response = self.generator(reflection)
                revised_contract = replace(
                    failed_action,
                    metadata={**failed_action.metadata, "reflection": reflection, "generator_response": response},
                )
                candidates.append(
                    ReplanCandidate(
                        action=revised_contract,
                        score=0.9,
                        rationale=f"LLM-generated correction from reflection: {response[:100]}",
                    )
                )
            except Exception:
                pass

        args = dict(failed_action.arguments)
        cmd = str(args.get("command", ""))
        operation = failed_action.operation.lower()

        if "rm" in operation or "delete" in operation or "rm " in cmd:
            safe_args = dict(args)
            safe_args["command"] = ["bash", "-lc", "ls -la"]
            candidates.append(
                ReplanCandidate(
                    action=replace(
                        failed_action,
                        operation="ls",
                        arguments=safe_args,
                        intent=f"Inspect target safely instead of destructive deletion ({reason})",
                        reversible=True,
                    ),
                    score=0.85,
                    rationale="Transformed irreversible deletion into safe inspection",
                )
            )

        if "calc" in failed_action.tool or "math" in failed_action.tool:
            candidates.append(
                ReplanCandidate(
                    action=replace(
                        failed_action,
                        intent=f"Recalculate expression with verified steps ({reason})",
                        metadata={**failed_action.metadata, "replan_reason": reason},
                    ),
                    score=0.80,
                    rationale="Structured recalculation step following arithmetic failure",
                )
            )

        if not candidates:
            candidates.append(
                ReplanCandidate(
                    action=replace(
                        failed_action,
                        intent=f"Reflective recovery: inspect status after error ({reason})",
                        metadata={**failed_action.metadata, "reflection": reflection},
                    ),
                    score=0.50,
                    rationale=f"Default reflective recovery probe: {reason}",
                )
            )

        return candidates[: self.max_candidates]
