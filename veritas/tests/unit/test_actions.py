import unittest

from veritas.actions.classes import ActionClass
from veritas.actions.contracts import ActionContract, Provenance
from veritas.actions.permissions import PermissionPolicy


class ActionTests(unittest.TestCase):
    def test_action_contract_classifies_mutating_edit(self) -> None:
        action = ActionContract(
            tool="fs",
            operation="write",
            arguments={"path": "x.py", "content": "print(1)"},
            intent="edit code",
            expected_effects=("workspace modified",),
            permissions_required=("workspace:read", "workspace:write"),
        )

        self.assertEqual(action.action_class, ActionClass.CODE_EDIT)
        self.assertTrue(action.mutates_state)

    def test_permission_policy_blocks_untrusted_privilege_escalation(self) -> None:
        action = ActionContract(
            tool="http",
            operation="post",
            arguments={"url": "https://example.test"},
            intent="send data",
            permissions_required=("network:external-post",),
            provenance=Provenance(("untrusted_tool",)),
        )
        policy = PermissionPolicy(granted_permissions=frozenset({"network:external-post"}))

        result = policy.validate(action)

        self.assertFalse(result.allowed)
        self.assertTrue(any("untrusted" in reason for reason in result.reasons))
