import os
import requests
from dotenv import load_dotenv
load_dotenv()

class BaseAgent:
    MODEL = "llama-3.3-70b-versatile"
    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, name, system_prompt):
        self.name = name
        self.system_prompt = system_prompt
        self.api_key = os.environ.get("GROQ_API_KEY", "")

    def call_glm(self, user_message, skill_context=""):
        system = self.system_prompt
        if skill_context:
            system = f"{system}\n\n## Skill Context\n{skill_context}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_message}],
            "max_tokens": 1024,
            "temperature": 0.3,
        }
        try:
            resp = requests.post(self.API_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[ERROR] {str(e)}"

    def run(self, user_input, skill_context=""):
        return self.call_glm(user_input, skill_context=skill_context)
