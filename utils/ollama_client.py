"""
utils/ollama_client.py
Thin wrapper around the Ollama HTTP API.
Handles JSON-mode enforcement and retry logic.
"""

import json
import re
import time
import requests
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaClient:
    def __init__(self, model: str, timeout: int = 120):
        self.model = model
        self.timeout = timeout

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        expect_json: bool = True,
        max_retries: int = 3,
    ) -> dict | str:
        """
        Send a chat request to Ollama.
        If expect_json=True, parses and returns a dict.
        Retries up to max_retries times on failure.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.2},
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                content = response.json()["message"]["content"]

                if expect_json:
                    return self._parse_json(content, attempt, max_retries)
                return content

            except requests.exceptions.ConnectionError:
                raise RuntimeError(
                    "Cannot connect to Ollama. Make sure Ollama is running: `ollama serve`"
                )
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    print(f"  [Timeout on attempt {attempt}, retrying...]")
                    time.sleep(2)
                else:
                    raise RuntimeError(f"Ollama timed out after {max_retries} attempts.")
            except (KeyError, json.JSONDecodeError) as e:
                if attempt < max_retries:
                    print(f"  [Parse error on attempt {attempt}, retrying...]")
                    time.sleep(1)
                else:
                    raise RuntimeError(f"Failed to parse Ollama response: {e}")

    def _parse_json(self, content: str, attempt: int, max_retries: int) -> dict:
        """Extract JSON from model output, handling markdown code fences."""
        # Strip <think>...</think> blocks (DeepSeek-r1 reasoning traces)
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try extracting from ```json ... ``` block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try finding first { ... } block
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError(f"No valid JSON found in response", content, 0)

    def check_model_available(self) -> bool:
        """Check if the configured model is pulled and available."""
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
            models = [m["name"] for m in r.json().get("models", [])]
            # Match on base name (ignore :latest tag variants)
            base = self.model.split(":")[0]
            return any(base in m for m in models)
        except Exception:
            return False
