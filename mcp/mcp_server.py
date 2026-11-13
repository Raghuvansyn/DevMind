from pathlib import Path
import re

SKILLS_DIR = Path(__file__).parent.parent / "skills"

class MCPServer:
    """Local skill/file helper; this class does not implement the MCP protocol."""

    MAX_FILE_BYTES = 100000

    def __init__(self, workspace=None):
        self._cache = {}
        self.workspace = Path(workspace or Path.cwd()).resolve()

    def get_skill_context(self, agent_name):
        if not isinstance(agent_name, str) or not re.fullmatch(r"[a-z_]+", agent_name):
            return ""
        if agent_name in self._cache:
            return self._cache[agent_name]
        skill_path = SKILLS_DIR / agent_name / "SKILL.md"
        if not skill_path.exists():
            return ""
        content = skill_path.read_text(encoding="utf-8")
        self._cache[agent_name] = content
        return content

    def read_file(self, file_path):
        """Read an allowed UTF-8 file contained in the configured workspace."""
        allowed = {".py", ".js", ".ts", ".json", ".md", ".txt", ".yaml"}
        try:
            path = (self.workspace / file_path).resolve()
        except (OSError, RuntimeError, TypeError, ValueError):
            return "[ERROR] Invalid file path."
        if not path.is_relative_to(self.workspace):
            return "[SECURITY] File must be inside the configured workspace."
        if path.suffix not in allowed:
            return f"[BLOCKED] File type {path.suffix} not allowed."
        try:
            if not path.is_file():
                return "[ERROR] File not found or not a regular file."
            with path.open("rb") as source:
                content = source.read(self.MAX_FILE_BYTES + 1)
            if len(content) > self.MAX_FILE_BYTES:
                return f"[BLOCKED] File exceeds {self.MAX_FILE_BYTES} bytes."
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return "[ERROR] File must contain UTF-8 text."
        except OSError:
            return "[ERROR] File could not be read."
