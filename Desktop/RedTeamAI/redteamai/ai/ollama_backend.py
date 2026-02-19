"""Ollama backend via /v1/chat/completions (OpenAI-compat)."""
from __future__ import annotations
import json
import re
import uuid
import asyncio
from typing import AsyncIterator, Any
import httpx
from redteamai.ai.base import AIBackend, AIResponse, ToolCall
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


class OllamaBackend(AIBackend):
    def __init__(self, host: str, model: str, timeout: int = 120, use_xml_fallback: bool = True):
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._use_xml_fallback = use_xml_fallback

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    async def health_check(self) -> tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{self._host}/api/tags")
                if r.status_code == 200:
                    data = r.json()
                    models = [m["name"] for m in data.get("models", [])]
                    if self._model in models or any(self._model in m for m in models):
                        return True, f"Ollama OK - {self._model} available"
                    return True, f"Ollama running but model '{self._model}' not pulled. Run: ollama pull {self._model}"
        except Exception as e:
            return False, f"Ollama not reachable at {self._host}: {e}"
        return False, "Unexpected response from Ollama"

    async def chat(self, messages: list[dict], tools: list[dict] | None = None, *, stream: bool = False) -> AIResponse:
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(f"{self._host}/v1/chat/completions", json=payload)
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

        choice = data["choices"][0]
        msg = choice["message"]
        content = msg.get("content") or ""
        raw_tool_calls = msg.get("tool_calls") or []

        tool_calls = [
            ToolCall(
                id=tc.get("id", str(uuid.uuid4())),
                name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"],
            )
            for tc in raw_tool_calls
        ]

        # XML fallback for models without native tool calling
        if not tool_calls and tools and self._use_xml_fallback and content:
            tool_calls = _parse_xml_tool_calls(content)

        return AIResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", "stop"),
            model=data.get("model", self._model),
            usage=data.get("usage", {}),
        )

    async def stream_chat(self, messages: list[dict], tools: list[dict] | None = None) -> AsyncIterator[str | ToolCall]:
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        full_content = ""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", f"{self._host}/v1/chat/completions", json=payload) as r:
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
                            full_content += token
                            yield token
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama streaming failed: {e}") from e

        # XML fallback after full stream
        if tools and self._use_xml_fallback and full_content:
            for tc in _parse_xml_tool_calls(full_content):
                yield tc


def _parse_xml_tool_calls(content: str) -> list[ToolCall]:
    """Fallback: parse <tool_call>{"name": ..., "arguments": ...}</tool_call> tags."""
    pattern = re.compile(r'<tool_call>(.*?)</tool_call>', re.DOTALL)
    tool_calls = []
    for m in pattern.finditer(content):
        try:
            data = json.loads(m.group(1).strip())
            tc = ToolCall(
                id=str(uuid.uuid4()),
                name=data.get("name", ""),
                arguments=data.get("arguments", data.get("parameters", {})),
            )
            if tc.name:
                tool_calls.append(tc)
        except (json.JSONDecodeError, KeyError):
            continue
    return tool_calls
