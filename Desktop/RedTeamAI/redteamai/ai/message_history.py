"""Message history management with token pruning."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MessageHistory:
    """Manages the conversation history for the AI agent."""
    max_tokens: int = 8000
    system_prompt: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str, tool_calls: list[dict] | None = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def add_tool_result(self, tool_call_id: str, tool_name: str, content: str) -> None:
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": content[:4000],  # Truncate very long tool outputs
        })

    def get_messages(self) -> list[dict]:
        """Return messages with system prompt prepended."""
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        msgs.extend(self.messages)
        return msgs

    def prune(self) -> None:
        """Remove oldest non-system messages if estimated token count exceeds limit."""
        # Simple heuristic: ~4 chars per token
        while self._estimate_tokens() > self.max_tokens and len(self.messages) > 2:
            # Always keep the last user message
            self.messages.pop(0)

    def _estimate_tokens(self) -> int:
        total = len(self.system_prompt) // 4
        for msg in self.messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += len(content) // 4
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        total += len(str(block)) // 4
        return total

    def clear(self) -> None:
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
