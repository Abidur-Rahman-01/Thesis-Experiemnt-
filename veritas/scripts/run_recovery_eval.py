"""Exercise checkpoint restore on a toy filesystem fault."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from veritas.actions.contracts import ActionContract
from veritas.sandbox.base import LocalWorkspaceSandbox
from veritas.sandbox.checkpoint import hash_directory


def main() -> None:
    with TemporaryDirectory() as tmp:
        sandbox = LocalWorkspaceSandbox(Path(tmp))
        sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "file.txt", "content": "good"}, intent="seed"))
        checkpoint = sandbox.checkpoint()
        sandbox.execute(ActionContract(tool="fs", operation="write", arguments={"path": "file.txt", "content": "bad"}, intent="inject bad patch"))
        mutated_hash = hash_directory(tmp, ignore_names={".veritas_checkpoints"})
        restored_hash = sandbox.restore(checkpoint)
        print(
            json.dumps(
                {
                    "checkpoint_hash": checkpoint.state_hash,
                    "mutated_hash": mutated_hash,
                    "restored_hash": restored_hash,
                    "restored": restored_hash == checkpoint.state_hash,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
