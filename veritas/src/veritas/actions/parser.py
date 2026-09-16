"""Parsing helpers for action contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from veritas.actions.contracts import ActionContract


def parse_action(data: str | dict) -> ActionContract:
    if isinstance(data, str):
        data = json.loads(data)
    if not isinstance(data, dict):
        raise TypeError("action data must be a JSON object or mapping")
    return ActionContract.from_mapping(data)


def load_jsonl(path: str | Path) -> list[ActionContract]:
    contracts: list[ActionContract] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                contracts.append(parse_action(line))
    return contracts


def dump_jsonl(contracts: Iterable[ActionContract], path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for contract in contracts:
            handle.write(json.dumps(contract.to_dict(), sort_keys=True) + "\n")
