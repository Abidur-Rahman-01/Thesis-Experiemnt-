"""Small CLI for the local VERITAS demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from veritas.actions.contracts import ActionContract
from veritas.actions.permissions import PermissionPolicy
from veritas.core.orchestrator import RuntimeConfig, VeritasRuntime
from veritas.models.local import HeuristicErrorEstimator
from veritas.models.provider import ScriptedPolicy
from veritas.risk.recovery_stats import RecoveryStatsTable
from veritas.risk.verifier_stats import VerifierStatsTable
from veritas.sandbox.base import LocalWorkspaceSandbox
from veritas.verification.action_falsifier import ActionFalsifier
from veritas.verification.deterministic import DeterministicVerifier


def build_demo_runtime(workspace: Path) -> VeritasRuntime:
    actions = [
        ActionContract(
            tool="fs",
            operation="write",
            arguments={"path": "answer.txt", "content": "verified\n"},
            intent="write toy project result",
            expected_effects=("workspace modified",),
            resources=("answer.txt",),
            permissions_required=("workspace:read", "workspace:write"),
            reversible=True,
            rollback_strategy="filesystem_checkpoint",
        )
    ]
    permissions = PermissionPolicy(
        granted_permissions=frozenset({"workspace:read", "workspace:write"}),
        allowed_tools=frozenset({"fs", "shell.exec"}),
    )
    return VeritasRuntime(
        policy=ScriptedPolicy(actions),
        error_estimator=HeuristicErrorEstimator(),
        sandbox=LocalWorkspaceSandbox(workspace),
        permission_policy=permissions,
        falsifier=ActionFalsifier(DeterministicVerifier(permissions)),
        verifier_stats=VerifierStatsTable.from_mapping({"default": {"detection_rate": 0.75, "false_positive_rate": 0.05}}),
        recovery_stats=RecoveryStatsTable.from_mapping({"default": {"residual_loss": 0.2}}),
        config=RuntimeConfig(max_steps=5, verification_budget=1.0, verification_cost=0.03),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="VERITAS research runtime")
    parser.add_argument("--demo", action="store_true", help="run a local toy VERITAS trajectory")
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        return

    with TemporaryDirectory() as tmp:
        runtime = build_demo_runtime(Path(tmp))
        state = runtime.run("write a toy result")
        print(json.dumps({"status": state.termination_status, "events": [event.to_dict() for event in state.actions]}, indent=2))


if __name__ == "__main__":
    main()
