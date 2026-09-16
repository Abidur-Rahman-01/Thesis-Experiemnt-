"""Action taxonomy used by VERITAS Paper 1 replay and statistics."""

from __future__ import annotations

from enum import Enum
from typing import Protocol


class ActionClass(str, Enum):
    READ = "read"
    SEARCH = "search"
    CODE_EDIT = "code_edit"
    SHELL = "shell"
    TEST = "test"
    DEPENDENCY_CHANGE = "dependency_change"
    DESTRUCTIVE_FILESYSTEM = "destructive_filesystem"
    EXTERNAL_MUTATION = "external_mutation"
    UNKNOWN = "unknown"


class ContractLike(Protocol):
    tool: str
    operation: str
    arguments: dict
    expected_effects: list[str]


DESTRUCTIVE_WORDS = ("delete", "remove", "rm", "rmdir", "drop", "truncate", "reset", "clean")
DEPENDENCY_WORDS = ("pip install", "npm install", "poetry add", "uv add", "conda install", "requirements")
TEST_WORDS = ("test", "pytest", "unittest", "mvn test", "gradle test", "cargo test", "go test")
READ_WORDS = ("read", "cat", "less", "head", "tail", "show", "inspect", "ls")
SEARCH_WORDS = ("search", "grep", "rg", "find")
EDIT_WORDS = ("write", "edit", "patch", "apply", "replace", "append", "modify")
EXTERNAL_WORDS = ("post", "send", "publish", "push", "deploy", "email", "payment", "api_call")


def classify_action(contract: ContractLike) -> ActionClass:
    text = " ".join(
        [
            contract.tool,
            contract.operation,
            " ".join(contract.expected_effects),
            str(contract.arguments.get("command", "")),
        ]
    ).lower()

    if any(word in text for word in DESTRUCTIVE_WORDS):
        return ActionClass.DESTRUCTIVE_FILESYSTEM
    if any(word in text for word in EXTERNAL_WORDS):
        return ActionClass.EXTERNAL_MUTATION
    if any(word in text for word in DEPENDENCY_WORDS):
        return ActionClass.DEPENDENCY_CHANGE
    if any(word in text for word in TEST_WORDS):
        return ActionClass.TEST
    if any(word in text for word in EDIT_WORDS):
        return ActionClass.CODE_EDIT
    if any(word in text for word in SEARCH_WORDS):
        return ActionClass.SEARCH
    if any(word in text for word in READ_WORDS):
        return ActionClass.READ
    if "shell" in contract.tool.lower():
        return ActionClass.SHELL
    return ActionClass.UNKNOWN


def is_state_mutating(action_class: ActionClass) -> bool:
    return action_class in {
        ActionClass.CODE_EDIT,
        ActionClass.SHELL,
        ActionClass.DEPENDENCY_CHANGE,
        ActionClass.DESTRUCTIVE_FILESYSTEM,
        ActionClass.EXTERNAL_MUTATION,
    }
