from agents.base_agent import BaseAgent

SYSTEM = """You are a senior code analyst. Review code for bugs, performance issues, and anti-patterns.
Always show: Issue → Explanation → Fix with before/after code examples."""

class CodeAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("code_analyst", SYSTEM)
    def run(self, user_input, skill_context=""):
        return f"[Code Analyst]\n{self.call_glm(user_input, skill_context)}"
