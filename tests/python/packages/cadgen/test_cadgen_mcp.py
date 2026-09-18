"""Unit tests for the local cadgen MCP tool wrappers (no stdio loop)."""

from __future__ import annotations

import unittest
from unittest import mock

from cadgen_mcp import server


class CadgenMcpTools(unittest.TestCase):
    def test_doctor_invokes_cadgen_cli(self) -> None:
        fake = mock.Mock(returncode=0, stdout="cadgen 0.6.5\n", stderr="")
        with mock.patch("cadgen_mcp.server.subprocess.run", return_value=fake) as run:
            result = server.tool_doctor()
        self.assertTrue(result["ok"])
        self.assertIn("doctor", result["cmd"])
        run.assert_called_once()

    def test_cadgen_refuses_daemon(self) -> None:
        result = server.tool_cadgen(["daemon"])
        self.assertFalse(result["ok"])
        self.assertIn("daemon", result["error"])

    def test_tool_schemas_include_core_verbs(self) -> None:
        names = {tool["name"] for tool in server._tool_schemas()}
        self.assertEqual(names, {"doctor", "snapshot", "step_snapshot", "viewer_url", "cadgen"})


if __name__ == "__main__":
    unittest.main()
