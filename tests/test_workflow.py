"""Offline checks: no real provider requests are made."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import requests

from agents.base_agent import BaseAgent
from mcp.mcp_server import MCPServer
from orchestrator import DevMindOrchestrator, route


def provider_response(body, status=200):
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps(body).encode("utf-8")
    return response


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"GROQ_API_KEY": "fixture-key"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def orchestrator(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return DevMindOrchestrator()

    @patch("agents.base_agent.requests.post")
    def test_complete_request_flow(self, post):
        post.return_value = provider_response({"choices": [{"message": {"content": " Fixture response "}}]})
        orch = self.orchestrator()
        with contextlib.redirect_stdout(io.StringIO()):
            output = orch.run("Write a docstring for def add(a, b): return a + b")
        self.assertEqual(output, "[Doc Writer]\nFixture response")
        self.assertEqual(orch.history[0]["agent"], "doc_writer")
        self.assertEqual(orch.history[0]["status"], "completed")
        payload = post.call_args.kwargs["json"]
        self.assertIn("# Doc Writer Skill", payload["messages"][0]["content"])
        self.assertEqual(payload["messages"][1]["content"], orch.history[0]["input"])
        self.assertEqual(payload["model"], "llama-3.3-70b-versatile")
        self.assertEqual(post.call_args.kwargs["timeout"], 30)

    def test_routing_examples(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "routing_cases.json"
        for case in json.loads(path.read_text(encoding="utf-8")):
            with self.subTest(prompt=case["prompt"]):
                self.assertEqual(route(case["prompt"]), case["expected_agent"])

    @patch("agents.base_agent.requests.post")
    def test_security_request_accepts_exact_input_limit(self, post):
        post.return_value = provider_response({"choices": [{"message": {"content": "fixture"}}]})
        orch = self.orchestrator()
        prompt = "scan " + "x" * (BaseAgent.MAX_INPUT_CHARS - 5)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIn("Scan #1", orch.run(prompt))
        self.assertEqual(post.call_args.kwargs["json"]["messages"][1]["content"], prompt)

    @patch("agents.base_agent.requests.post")
    def test_blocked_request_never_calls_provider(self, post):
        orch = self.orchestrator()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIn("[BLOCKED]", orch.run("run rm -rf /"))
        post.assert_not_called()
        self.assertEqual(orch.history[0]["status"], "blocked")

    @patch("agents.base_agent.requests.post")
    def test_invalid_inputs_never_call_provider(self, post):
        orch = self.orchestrator()
        for value in (None, "", "   ", "x" * 20001):
            self.assertIn("[ERROR]", orch.run(value))
        post.assert_not_called()

    @patch("agents.base_agent.requests.post")
    def test_missing_or_placeholder_key_never_calls_provider(self, post):
        for key in ("", "your_groq_api_key_here", "   "):
            with patch.dict(os.environ, {"GROQ_API_KEY": key}):
                self.assertIn("Set GROQ_API_KEY", BaseAgent("test", "prompt").run("review"))
        post.assert_not_called()

    @patch("agents.base_agent.requests.post")
    def test_provider_failures_return_safe_errors(self, post):
        agent = BaseAgent("test", "prompt")
        for error, message in ((requests.Timeout("private details"), "timed out"),
                               (requests.ConnectionError("private details"), "Could not reach")):
            with self.subTest(error=type(error).__name__):
                post.side_effect = error
                result = agent.run("review")
                self.assertIn(message, result)
                self.assertNotIn("private details", result)
        post.side_effect = None
        for status, message in ((401, "credentials"), (403, "credentials"),
                                (429, "rate limit"), (503, "unsuccessful HTTP")):
            with self.subTest(status=status):
                post.return_value = provider_response({"error": "private details"}, status)
                result = agent.run("review")
                self.assertIn(message, result)
                self.assertNotIn("private details", result)

    @patch("agents.base_agent.requests.post")
    def test_malformed_provider_bodies(self, post):
        agent = BaseAgent("test", "prompt")
        for body in ({}, {"choices": []}, {"choices": [{"message": {"content": None}}]},
                     {"choices": [{"message": {"content": " "}}]}):
            with self.subTest(body=body):
                post.return_value = provider_response(body)
                self.assertIn("unexpected response format", agent.run("review"))
        post.return_value = provider_response({})
        post.return_value._content = b"not JSON"
        self.assertIn("unexpected response format", agent.run("review"))

    @patch("agents.base_agent.requests.post")
    def test_failed_call_is_recorded_as_error(self, post):
        post.side_effect = requests.Timeout()
        orch = self.orchestrator()
        with contextlib.redirect_stdout(io.StringIO()):
            orch.run("Review def add(a, b): return a+b")
        self.assertEqual(orch.history[0]["status"], "error")


class FileHelperTests(unittest.TestCase):
    def test_file_access_stays_in_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "example.py").write_text("print('safe sample')", encoding="utf-8")
            (root / "outside.txt").write_text("synthetic private data", encoding="utf-8")
            (workspace / "link.txt").symlink_to(root / "outside.txt")
            server = MCPServer(workspace)
            self.assertEqual(server.read_file("example.py"), "print('safe sample')")
            for path in ("../outside.txt", root / "outside.txt", "link.txt"):
                self.assertIn("[SECURITY]", server.read_file(path))
            self.assertIn("[BLOCKED]", server.read_file("image.png"))
            self.assertIn("[ERROR]", server.read_file("missing.py"))
            (workspace / "directory.py").mkdir()
            self.assertIn("[ERROR]", server.read_file("directory.py"))
            (workspace / "binary.txt").write_bytes(b"\xff")
            self.assertIn("UTF-8", server.read_file("binary.txt"))
            (workspace / "large.txt").write_bytes(b"x" * (server.MAX_FILE_BYTES + 1))
            self.assertIn("[BLOCKED]", server.read_file("large.txt"))

    def test_skills_are_selected_by_agent_name(self):
        server = MCPServer()
        for name in ("code_analyst", "doc_writer", "security_scan"):
            with self.subTest(name=name):
                self.assertIn("## Purpose", server.get_skill_context(name))
        self.assertEqual(server.get_skill_context("../../README"), "")
        self.assertEqual(server.get_skill_context("nonexistent"), "")


if __name__ == "__main__":
    unittest.main()
