"""Abstract base classes for AI backends."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class AIResponse:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"  # stop / tool_calls / length
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


class AIBackend(ABC):
    """Abstract base for all AI backends."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        *,
        stream: bool = False,
    ) -> AIResponse:
        """Send messages and return a complete response."""

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[str | ToolCall]:
        """Stream tokens and tool calls as they arrive."""

    @abstractmethod
    async def health_check(self) -> tuple[bool, str]:
        """Return (healthy, status_message)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier (e.g. 'ollama', 'groq')."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Active model name."""
