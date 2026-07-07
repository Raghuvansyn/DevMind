from agents.base_agent import BaseAgent

SYSTEM = """You are a technical documentation specialist. Generate clear docstrings, README files, and inline comments.
Use Google-style docstrings. README structure: Title, Overview, Install, Usage, Architecture."""

class DocWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("doc_writer", SYSTEM)
    def run(self, user_input, skill_context=""):
        return f"[Doc Writer]\n{self.call_glm(user_input, skill_context)}"
