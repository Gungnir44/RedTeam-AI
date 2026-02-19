"""Anthropic (Claude) backend."""
from __future__ import annotations
import json
import uuid
from typing import AsyncIterator
from redteamai.ai.base import AIBackend, AIResponse, ToolCall
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


class AnthropicBackend(AIBackend):
    def __init__(self, api_key: str, model: str, timeout: int = 120, max_tokens: int = 4096):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._max_tokens = max_tokens

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    def _get_client(self):
        try:
            import anthropic
            return anthropic.AsyncAnthropic(api_key=self._api_key)
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    async def health_check(self) -> tuple[bool, str]:
        if not self._api_key:
            return False, "No Anthropic API key configured"
        try:
            client = self._get_client()
            r = await client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True, f"Anthropic OK - {self._model}"
        except Exception as e:
            return False, f"Anthropic error: {e}"

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert OpenAI-style tools to Anthropic format."""
        converted = []
        for t in tools:
            if t.get("type") == "function":
                fn = t["function"]
                converted.append({
                    "name": fn["name"],
                    "description": fn.get("description", ""),
                    "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
                })
        return converted

    def _convert_messages(self, messages: list[dict]) -> tuple[str | None, list[dict]]:
        """Split system prompt and convert messages to Anthropic format."""
        system = None
        converted = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                system = msg["content"]
            elif role == "tool":
                converted.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.get("tool_call_id", ""),
                        "content": str(msg["content"]),
                    }]
                })
            elif role == "assistant" and msg.get("tool_calls"):
                content = []
                if msg.get("content"):
                    content.append({"type": "text", "text": msg["content"]})
                for tc in msg["tool_calls"]:
                    content.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "input": json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"],
                    })
                converted.append({"role": "assistant", "content": content})
            else:
                converted.append({"role": role, "content": msg["content"]})
        return system, converted

    async def chat(self, messages: list[dict], tools: list[dict] | None = None, *, stream: bool = False) -> AIResponse:
        client = self._get_client()
        system, converted = self._convert_messages(messages)
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": converted,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        r = await client.messages.create(**kwargs)

        content = ""
        tool_calls = []
        for block in r.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, arguments=block.input or {}))

        return AIResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason="tool_calls" if tool_calls else "stop",
            model=self._model,
        )

    async def stream_chat(self, messages: list[dict], tools: list[dict] | None = None) -> AsyncIterator[str | ToolCall]:
        client = self._get_client()
        system, converted = self._convert_messages(messages)
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": converted,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
