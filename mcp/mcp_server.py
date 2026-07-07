from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

class MCPServer:
    def __init__(self):
        self._cache = {}

    def get_skill_context(self, agent_name):
        if agent_name in self._cache:
            return self._cache[agent_name]
        skill_path = SKILLS_DIR / agent_name / "SKILL.md"
        if not skill_path.exists():
            return ""
        content = skill_path.read_text(encoding="utf-8")
        self._cache[agent_name] = content
        return content

    def read_file(self, file_path):
        allowed = {".py", ".js", ".ts", ".json", ".md", ".txt", ".yaml"}
        path = Path(file_path).resolve()
        if ".." in str(file_path):
            return "[SECURITY] Path traversal blocked."
        if path.suffix not in allowed:
            return f"[BLOCKED] File type {path.suffix} not allowed."
        if not path.exists():
            return f"[ERROR] File not found: {file_path}"
        return path.read_text(encoding="utf-8")
