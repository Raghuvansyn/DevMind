import re
from agents.base_agent import BaseAgent
from agents.code_analyst import CodeAnalystAgent
from agents.doc_writer import DocWriterAgent
from agents.security_scan import SecurityScanAgent
from mcp.mcp_server import MCPServer

BLOCKED = [r"(rm\s+-rf|sudo|eval\s*\(|exec\s*\(|__import__|os\.system)"]

def security_guard(text):
    for p in BLOCKED:
        if re.search(p, text, re.IGNORECASE):
            print("[SECURITY] Blocked dangerous input.")
            return False
    return True

def route(text):
    t = text.lower()
    if re.search(r"\b(security|vulnerabilit(?:y|ies)|scan|injection|exploit|safe)\b", t):
        return "security_scan"
    elif re.search(r"\b(document(?:ation)?|readme|docstrings?|comments?|docs)\b", t):
        return "doc_writer"
    return "code_analyst"

class DevMindOrchestrator:
    def __init__(self):
        self.agents = {
            "code_analyst": CodeAnalystAgent(),
            "doc_writer": DocWriterAgent(),
            "security_scan": SecurityScanAgent(),
        }
        self.mcp = MCPServer()
        self.history = []
        print("DevMind ready. Type 'exit' to quit, 'log' to see audit trail.")
        print("=" * 60)

    def run(self, user_input):
        if not isinstance(user_input, str) or not user_input.strip():
            return "[ERROR] Provide a non-empty text request."
        if len(user_input) > BaseAgent.MAX_INPUT_CHARS:
            return f"[ERROR] Request exceeds {BaseAgent.MAX_INPUT_CHARS} characters."
        if not security_guard(user_input):
            self.history.append({"input": user_input, "agent": None, "status": "blocked"})
            return "[BLOCKED] Input flagged by security guard."
        agent_name = route(user_input)
        print(f"[ORCHESTRATOR] Routing to: {agent_name}")
        skill_context = self.mcp.get_skill_context(agent_name)
        response = self.agents[agent_name].run(user_input, skill_context=skill_context)
        status = "error" if "[ERROR]" in response else "completed"
        self.history.append({"input": user_input, "agent": agent_name, "status": status})
        return response

    def show_log(self):
        print("\n[AUDIT LOG]")
        for i, e in enumerate(self.history):
            print(f"  {i+1}. agent={e['agent']} | status={e['status']} | input='{e['input'][:60]}'")

def main():
    orch = DevMindOrchestrator()
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            orch.show_log()
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit","quit","q"):
            orch.show_log()
            break
        if user_input.lower() == "log":
            orch.show_log()
            continue
        print(f"\nDevMind: {orch.run(user_input)}")

if __name__ == "__main__":
    main()
