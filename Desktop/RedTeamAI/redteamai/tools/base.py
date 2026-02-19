"""Base classes for all tool adapters."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    success: bool
    output: str
    error: str = ""
    raw_data: Any = None
    exit_code: int = 0


class BaseTool(ABC):
    """Abstract base for all tool adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier (snake_case)."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for AI tool manifest."""

    @property
    def binary(self) -> str:
        """The underlying binary name (for availability check)."""
        return ""

    @property
    def is_builtin(self) -> bool:
        """True if implemented in pure Python (no binary required)."""
        return False

    @property
    def is_dangerous(self) -> bool:
        """True if this tool requires user confirmation before running."""
        return False

    @abstractmethod
    def get_schema(self) -> dict:
        """Return OpenAI-compatible function calling schema."""

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool synchronously and return a ToolResult."""

    def get_command(self, **kwargs) -> list[str]:
        """Return the command list that would be run (for confirmation dialog)."""
        return []
