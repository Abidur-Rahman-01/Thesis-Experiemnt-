"""Import mini-SWE-agent trajectories into VERITAS action-level records."""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import replace
from pathlib import Path
from typing import Any

from veritas.actions.contracts import ActionContract, Provenance


_FENCED_COMMAND = re.compile(r"```(?:mswea_bash_command|bash|sh)\s*\n(.*?)```", re.DOTALL)
_RETURN_CODE = re.compile(r"<returncode>(-?\d+)</returncode>")
_OUTPUT = re.compile(r"<output>\s*(.*?)\s*</output>", re.DOTALL)


def load_miniswe_trajectory(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"messages": payload, "trajectory_format": "mini-swe-agent-legacy"}
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list):
        raise ValueError("mini-SWE-agent trajectory must contain a messages list")
    return payload


def _commands(message: dict[str, Any]) -> list[str]:
    actions = message.get("extra", {}).get("actions", [])
    commands = [action.get("command") for action in actions if isinstance(action, dict)]
    commands = [command for command in commands if isinstance(command, str) and command.strip()]
    if commands:
        return commands
    content = message.get("content", "")
    if isinstance(content, str):
        return [match.strip() for match in _FENCED_COMMAND.findall(content) if match.strip()]
    return []


def _operation(command: str) -> str:
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        parts = command.split()
    return parts[0] if parts else "shell"


def _tokens(extra: dict[str, Any]) -> tuple[int | None, int | None]:
    usage = extra.get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    input_tokens = usage.get("prompt_tokens", usage.get("input_tokens"))
    output_tokens = usage.get("completion_tokens", usage.get("output_tokens"))
    return _integer_or_none(input_tokens), _integer_or_none(output_tokens)


def _integer_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _failure_type(return_code: Any, exception: Any) -> str | None:
    if exception:
        return "environment_or_tool_failure"
    if return_code is None or return_code == 0:
        return None
    return "command_failure"


def _observation(message: dict[str, Any]) -> dict[str, Any] | None:
    extra = message.get("extra", {})
    if isinstance(extra, dict) and ("returncode" in extra or "raw_output" in extra):
        return extra
    content = message.get("content", "")
    if not isinstance(content, str):
        return None
    return_code_match = _RETURN_CODE.search(content)
    output_match = _OUTPUT.search(content)
    if return_code_match is None and output_match is None:
        return None
    return {
        "returncode": int(return_code_match.group(1)) if return_code_match else None,
        "raw_output": output_match.group(1) if output_match else "",
        "exception_info": None,
    }


def import_miniswe_trajectory(path: str | Path) -> list[dict[str, Any]]:
    """Create unscored action records; semantic labels must be added separately."""
    payload = load_miniswe_trajectory(path)
    messages = payload["messages"]
    info = payload.get("info", {}) if isinstance(payload.get("info", {}), dict) else {}
    task_id = str(payload.get("instance_id") or info.get("instance_id") or Path(path).stem)
    run_id = str(payload.get("run_id") or f"mini:{task_id}")
    final_outcome = str(info.get("exit_status", "unknown"))
    records: list[dict[str, Any]] = []

    for message_index, message in enumerate(messages):
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        commands = _commands(message)
        if not commands:
            continue
        extra = message.get("extra", {}) if isinstance(message.get("extra", {}), dict) else {}
        input_tokens, output_tokens = _tokens(extra)
        observations = []
        for candidate in messages[message_index + 1 :]:
            if not isinstance(candidate, dict):
                continue
            if candidate.get("role") == "assistant":
                break
            parsed_observation = _observation(candidate)
            if parsed_observation is not None:
                observations.append(parsed_observation)

        for action_offset, command in enumerate(commands):
            observation = observations[action_offset] if action_offset < len(observations) else {}
            return_code = observation.get("returncode")
            contract = ActionContract(
                tool="shell.exec",
                operation=_operation(command),
                arguments={"command": ["bash", "-lc", command]},
                intent="Imported mini-SWE-agent action",
                permissions_required=("workspace:read",),
                provenance=Provenance(("model_generated",)),
                rollback_strategy="restore_checkpoint",
                metadata={"source": "mini-swe-agent", "message_index": message_index},
            )
            if contract.mutates_state:
                contract = replace(contract, permissions_required=("workspace:read", "workspace:write"))
            records.append(
                {
                    "record_schema": "veritas.action.v1",
                    "task_id": task_id,
                    "run_id": run_id,
                    "step": len(records),
                    "history_reference": {"trajectory": str(Path(path)), "message_index": message_index},
                    "action_id": contract.action_id,
                    "action_json": contract.to_dict(),
                    "action_class": contract.action_class.value,
                    "raw_error_score": None,
                    "calibrated_error_probability": None,
                    "impact": None,
                    "verifier_verdict": None,
                    "verification_cost": None,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model_cost": extra.get("cost"),
                    "observation": observation.get("raw_output", ""),
                    "return_code": return_code,
                    "execution_success": return_code == 0 if return_code is not None else None,
                    "failure_type": _failure_type(return_code, observation.get("exception_info")),
                    "ground_truth_label": "unresolved",
                    "label_source": "unlabeled",
                    "final_task_outcome": final_outcome,
                    "source_trajectory_format": payload.get("trajectory_format", "unknown"),
                }
            )
    return records
