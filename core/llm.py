from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_MODEL = os.getenv("PROOFPRINT_MODEL", "gemma4:e2b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


class LocalGemmaClient:
    def __init__(self, model: str = DEFAULT_MODEL, url: str = OLLAMA_URL, timeout: int = 180) -> None:
        self.model = model
        self.url = url
        self.timeout = timeout

    def available(self) -> bool:
        tags_url = self.url.replace("/api/generate", "/api/tags")
        try:
            with urllib.request.urlopen(tags_url, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
            return any(model.get("name") == self.model or model.get("model") == self.model for model in body.get("models", []))
        except Exception:
            return False

    def generate(self, prompt: str, images: list[bytes] | None = None) -> tuple[str, str]:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "top_p": 0.9},
        }
        if images:
            payload["images"] = [base64.b64encode(image).decode("ascii") for image in images]

        try:
            request = urllib.request.Request(
                self.url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return body.get("response", "").strip(), f"local Gemma via Ollama ({self.model})"
        except urllib.error.HTTPError as exc:
            return "", f"Ollama HTTP error: {exc.code}"
        except Exception as exc:
            return "", f"Gemma unavailable ({exc.__class__.__name__})"


def extract_json_block(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
