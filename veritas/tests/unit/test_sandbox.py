from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from veritas.actions.contracts import ActionContract
from veritas.sandbox.base import LocalWorkspaceSandbox


class LocalSandboxTests(unittest.TestCase):
    def test_shell_uses_argument_list_with_current_python(self) -> None:
        with TemporaryDirectory() as tmp:
            sandbox = LocalWorkspaceSandbox(Path(tmp))
            action = ActionContract(
                tool="shell.exec",
                operation="run",
                arguments={"command": [sys.executable, "-c", "print('portable')"]},
                intent="cross-platform subprocess check",
            )

            result = sandbox.execute(action)

            self.assertTrue(result.ok)
            self.assertEqual(result.output.strip(), "portable")

    def test_missing_executable_returns_structured_failure(self) -> None:
        with TemporaryDirectory() as tmp:
            sandbox = LocalWorkspaceSandbox(Path(tmp))
            action = ActionContract(
                tool="shell.exec",
                operation="run",
                arguments={"command": ["veritas-command-that-does-not-exist"]},
                intent="exercise process startup failure",
            )

            result = sandbox.execute(action)

            self.assertFalse(result.ok)
            self.assertEqual(result.return_code, 127)
            self.assertIn("could not start command", result.error)

    def test_filesystem_path_escape_is_blocked(self) -> None:
        with TemporaryDirectory() as tmp:
            sandbox = LocalWorkspaceSandbox(Path(tmp))
            action = ActionContract(
                tool="fs",
                operation="write",
                arguments={"path": "../outside.txt", "content": "blocked"},
                intent="exercise containment",
            )

            result = sandbox.execute(action)

            self.assertFalse(result.ok)
            self.assertIn("escapes workspace", result.error)


if __name__ == "__main__":
    unittest.main()
