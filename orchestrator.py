import re
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
    if any(k in t for k in ["security","vulnerability","scan","injection","exploit","safe"]):
        return "security_scan"
    elif any(k in t for k in ["document","readme","docstring","comment","docs"]):
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
        if not security_guard(user_input):
            return "[BLOCKED] Input flagged by security guard."
        agent_name = route(user_input)
        print(f"[ORCHESTRATOR] Routing to: {agent_name}")
        skill_context = self.mcp.get_skill_context(agent_name)
        response = self.agents[agent_name].run(user_input, skill_context=skill_context)
        self.history.append({"input": user_input, "agent": agent_name})
        return response

    def show_log(self):
        print("\n[AUDIT LOG]")
        for i, e in enumerate(self.history):
            print(f"  {i+1}. agent={e['agent']} | input='{e['input'][:60]}'")

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
