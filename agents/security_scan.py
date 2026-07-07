from agents.base_agent import BaseAgent

SYSTEM = """You are a security analyst. Identify OWASP Top 10 vulnerabilities.
Format: RISK LEVEL → VULNERABILITY → LOCATION → DESCRIPTION → RECOMMENDATION with secure code example."""

class SecurityScanAgent(BaseAgent):
    def __init__(self):
        super().__init__("security_scan", SYSTEM)
        self._scan_count = 0
    def run(self, user_input, skill_context=""):
        self._scan_count += 1
        return f"[Security Scanner | Scan #{self._scan_count}]\n{self.call_glm(f'SCAN #{self._scan_count}\n{user_input}', skill_context)}"
