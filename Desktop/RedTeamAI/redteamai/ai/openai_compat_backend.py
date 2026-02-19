"""OpenAI-compatible backend (any endpoint: OpenAI, LM Studio, Together, etc.)."""
from __future__ import annotations
import json
import uuid
from typing import AsyncIterator
import httpx
from redteamai.ai.base import AIBackend, AIResponse, ToolCall
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


class OpenAICompatBackend(AIBackend):
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 120):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "openai_compat"

    @property
    def model(self) -> str:
        return self._model

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    async def health_check(self) -> tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{self._base_url}/models", headers=self._headers())
                if r.status_code in (200, 401):  # 401 means reachable but needs auth
                    return r.status_code == 200, f"OpenAI-compat OK - {self._model}"
                return False, f"HTTP {r.status_code} from {self._base_url}"
        except Exception as e:
            return False, f"Not reachable: {e}"

    async def chat(self, messages: list[dict], tools: list[dict] | None = None, *, stream: bool = False) -> AIResponse:
        payload: dict = {"model": self._model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(f"{self._base_url}/chat/completions", json=payload, headers=self._headers())
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

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream("POST", f"{self._base_url}/chat/completions", json=payload, headers=self._headers()) as r:
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
