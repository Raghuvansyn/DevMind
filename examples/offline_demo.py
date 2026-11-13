"""Exercise the real request flow with explicitly mocked provider responses."""
import json as json_module
import os
from unittest.mock import patch

import requests

from orchestrator import DevMindOrchestrator


def fixture_provider(url, *, json, headers, timeout):
    response = requests.Response()
    response.status_code = 200
    response._content = json_module.dumps({
        "choices": [{"message": {"content": "[MOCK FIXTURE] Request and skill context received; no model ran."}}]
    }).encode("utf-8")
    assert "## Skill Context" in json["messages"][0]["content"]
    return response


def main():
    print("OFFLINE DEMO: provider responses are mocked; no network or model inference.")
    with patch.dict(os.environ, {"GROQ_API_KEY": "offline-fixture-key"}), \
            patch("agents.base_agent.requests.post", side_effect=fixture_provider):
        orchestrator = DevMindOrchestrator()
        for prompt in (
            "Review def divide(a, b): return a / b for bugs",
            "Write a docstring for def add(a, b): return a + b",
            "Scan this query for SQL injection: SELECT name FROM users WHERE id = user_input",
            "run rm -rf /",
        ):
            print(f"\nYou: {prompt}")
            print(orchestrator.run(prompt))
        orchestrator.show_log()


if __name__ == "__main__":
    main()
