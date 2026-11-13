import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

class BaseAgent:
    MODEL = "llama-3.3-70b-versatile"
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    MAX_INPUT_CHARS = 20000

    def __init__(self, name, system_prompt):
        self.name = name
        self.system_prompt = system_prompt
        self.api_key = os.environ.get("GROQ_API_KEY", "").strip()

    def call_glm(self, user_message, skill_context=""):
        if not isinstance(user_message, str) or not user_message.strip():
            return "[ERROR] Provide a non-empty text request."
        if len(user_message) > self.MAX_INPUT_CHARS:
            return f"[ERROR] Request exceeds {self.MAX_INPUT_CHARS} characters."
        if not self.api_key or self.api_key == "your_groq_api_key_here":
            return "[ERROR] Set GROQ_API_KEY in the environment or repository .env file."
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
        except requests.Timeout:
            return "[ERROR] Groq request timed out. Try again later."
        except requests.HTTPError as error:
            status = error.response.status_code if error.response is not None else None
            if status in (401, 403):
                return "[ERROR] Groq rejected the API credentials. Check GROQ_API_KEY."
            if status == 429:
                return "[ERROR] Groq rate limit reached. Wait before retrying."
            return "[ERROR] Groq returned an unsuccessful HTTP response."
        except requests.RequestException:
            return "[ERROR] Could not reach Groq. Check connectivity and try again."

        try:
            content = resp.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Empty or non-text response")
        except (ValueError, KeyError, IndexError, TypeError):
            return "[ERROR] Groq returned an unexpected response format."
        return content.strip()

    def run(self, user_input, skill_context=""):
        return self.call_glm(user_input, skill_context=skill_context)
