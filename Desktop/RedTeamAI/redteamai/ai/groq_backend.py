"""Groq backend (free tier, fast inference)."""
from __future__ import annotations
import json
import uuid
from typing import AsyncIterator
import httpx
from redteamai.ai.base import AIBackend, AIResponse, ToolCall
from redteamai.utils.logger import get_logger

log = get_logger(__name__)
GROQ_BASE = "https://api.groq.com/openai/v1"


class GroqBackend(AIBackend):
    def __init__(self, api_key: str, model: str, timeout: int = 60):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model(self) -> str:
        return self._model

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    async def health_check(self) -> tuple[bool, str]:
        if not self._api_key:
            return False, "No Groq API key configured"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{GROQ_BASE}/models", headers=self._headers())
                if r.status_code == 200:
                    return True, f"Groq OK - model: {self._model}"
                return False, f"Groq returned HTTP {r.status_code}"
        except Exception as e:
            return False, f"Groq not reachable: {e}"

    async def chat(self, messages: list[dict], tools: list[dict] | None = None, *, stream: bool = False) -> AIResponse:
        payload: dict = {"model": self._model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(f"{GROQ_BASE}/chat/completions", json=payload, headers=self._headers())
            r.raise_for_status()
            data = r.json()

        choice = data["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""
        raw_tcs = msg.get("tool_calls") or []
        tool_calls = [
            ToolCall(
                id=tc.get("id", str(uuid.uuid4())),
                name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"],
            )
            for tc in raw_tcs
        ]
        return AIResponse(content=content, tool_calls=tool_calls, finish_reason=choice.get("finish_reason", "stop"), model=self._model)

    async def stream_chat(self, messages: list[dict], tools: list[dict] | None = None) -> AsyncIterator[str | ToolCall]:
        payload: dict = {"model": self._model, "messages": messages, "stream": True}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", f"{GROQ_BASE}/chat/completions", json=payload, headers=self._headers()) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    if raw == "[DONE]":
                        break
                    try:
                        chunk = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content") or ""
                    if token:
                        yield token
