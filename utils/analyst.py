from __future__ import annotations

"""AI analyst integration for Pentest-Toolkit."""

import json
import os
from typing import List, Dict, Any

import requests

from utils.logger import get_logger
from modules.base import Finding

logger = get_logger()


class LLMClient:
    """Minimal client for local or remote LLMs."""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_BASE_URL")
        self.custom_endpoint = os.environ.get("LLM_ENDPOINT")

    def analyse(self, findings: List[Finding]) -> str:
        """Return a summary string for *findings* using the configured LLM."""
        payload = json.dumps([f.asdict() for f in findings], indent=2)
        if self.ollama_url:
            url = self.ollama_url.rstrip("/") + "/api/chat"
            data = {"model": self.model, "messages": [{"role": "user", "content": payload}]}
            return self._post(url, data)
        endpoint = self.custom_endpoint or "https://api.openai.com/v1/chat/completions"
        headers: Dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = {"model": self.model, "messages": [{"role": "user", "content": payload}]}
        return self._post(endpoint, data, headers=headers)

    def _post(self, url: str, data: Dict[str, Any], headers: Dict[str, str] | None = None) -> str:
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=60)
            resp.raise_for_status()
            out = resp.json()
            if isinstance(out, dict) and out.get("choices"):
                return out["choices"][0]["message"]["content"]
            return resp.text
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM request failed: %s", exc)
            return "AI analysis failed"


def analyse_findings(findings: List[Finding]) -> str:
    """Convenience wrapper using :class:`LLMClient`."""
    client = LLMClient()
    return client.analyse(findings)
