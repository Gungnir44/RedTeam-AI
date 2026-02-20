"""Ollama backend via /api/chat (native Ollama endpoint, supports local and cloud models)."""
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

    @staticmethod
    def _normalize_messages(messages: list[dict]) -> list[dict]:
        """Convert OpenAI-format messages to Ollama native /api/chat format.

        Key differences:
        - tool_calls arguments must be a dict, not a JSON string
        - tool_calls must not have 'type' key
        - tool result messages must not have 'tool_call_id' or 'name'
        """
        out = []
        for msg in messages:
            msg = dict(msg)
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                normalized_calls = []
                for tc in msg["tool_calls"]:
                    tc = dict(tc)
                    tc.pop("type", None)
                    fn = dict(tc.get("function", {}))
                    args = fn.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    fn["arguments"] = args
                    tc["function"] = fn
                    normalized_calls.append(tc)
                msg["tool_calls"] = normalized_calls
            elif msg.get("role") == "tool":
                msg.pop("tool_call_id", None)
                msg.pop("name", None)
            out.append(msg)
        return out

    async def chat(self, messages: list[dict], tools: list[dict] | None = None, *, stream: bool = False) -> AIResponse:
        payload = {
            "model": self._model,
            "messages": self._normalize_messages(messages),
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(f"{self._host}/api/chat", json=payload)
                r.raise_for_status()
                data = r.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

        msg = data.get("message", {})
        content = msg.get("content") or ""
        raw_tool_calls = msg.get("tool_calls") or []

        tool_calls = [
            ToolCall(
                id=str(uuid.uuid4()),
                name=tc["function"]["name"],
                arguments=tc["function"]["arguments"] if isinstance(tc["function"]["arguments"], dict) else json.loads(tc["function"]["arguments"]),
            )
            for tc in raw_tool_calls
        ]

        # XML fallback for models without native tool calling
        if not tool_calls and tools and self._use_xml_fallback and content:
            tool_calls = _parse_xml_tool_calls(content)

        return AIResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=data.get("done_reason", "stop"),
            model=data.get("model", self._model),
            usage={},
        )

    async def stream_chat(self, messages: list[dict], tools: list[dict] | None = None) -> AsyncIterator[str | ToolCall]:
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        payload["messages"] = self._normalize_messages(payload["messages"])
        full_content = ""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", f"{self._host}/api/chat", json=payload) as r:
                    r.raise_for_status()
                    async for line in r.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        msg = chunk.get("message", {})
                        token = msg.get("content") or ""
                        if token:
                            full_content += token
                            yield token
                        # Tool calls can arrive in any chunk (not just the done chunk)
                        for tc_raw in (msg.get("tool_calls") or []):
                            fn = tc_raw.get("function", {})
                            args = fn.get("arguments", {})
                            if isinstance(args, str):
                                args = json.loads(args)
                            yield ToolCall(
                                id=tc_raw.get("id", str(uuid.uuid4())),
                                name=fn.get("name", ""),
                                arguments=args,
                            )
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
