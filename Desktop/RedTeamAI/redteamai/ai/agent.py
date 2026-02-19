"""ReAct loop agent: Reasoning + Acting with typed AgentEvents."""
from __future__ import annotations
import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Optional

from redteamai.ai.base import AIBackend, ToolCall
from redteamai.ai.message_history import MessageHistory
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


# ── Agent Events ──────────────────────────────────────────────────────────────

@dataclass
class TextChunkEvent:
    text: str

@dataclass
class ThinkingEvent:
    text: str

@dataclass
class ToolCallEvent:
    tool_name: str
    arguments: dict
    call_id: str

@dataclass
class ToolResultEvent:
    tool_name: str
    call_id: str
    output: str
    error: bool = False

@dataclass
class ConfirmationRequiredEvent:
    tool_name: str
    command: str
    call_id: str
    # The agent will wait on this event
    confirm_event: asyncio.Event = field(default_factory=asyncio.Event)
    confirmed: bool = False

@dataclass
class AgentDoneEvent:
    final_response: str
    iterations: int

@dataclass
class AgentErrorEvent:
    error: str


AgentEvent = (
    TextChunkEvent | ThinkingEvent | ToolCallEvent | ToolResultEvent |
    ConfirmationRequiredEvent | AgentDoneEvent | AgentErrorEvent
)

# ── Dangerous tool detection ──────────────────────────────────────────────────
DANGEROUS_TOOLS = {"metasploit_exec", "exploit_run", "ffuf", "gobuster"}

# ── Agent ─────────────────────────────────────────────────────────────────────

class RedTeamAgent:
    """
    ReAct loop agent. Yields AgentEvent objects.
    Tool executor is an async callable: (tool_name, args) -> str
    """

    def __init__(
        self,
        backend: AIBackend,
        tool_executor: Callable[[str, dict], Any],
        tools_manifest: list[dict],
        history: MessageHistory,
        max_iterations: int = 10,
        require_confirm_dangerous: bool = True,
    ):
        self.backend = backend
        self.tool_executor = tool_executor
        self.tools_manifest = tools_manifest
        self.history = history
        self.max_iterations = max_iterations
        self.require_confirm = require_confirm_dangerous

    async def run(self, user_message: str) -> AsyncIterator[AgentEvent]:
        """Run the ReAct loop for a user message, yielding events."""
        self.history.add_user(user_message)
        self.history.prune()

        final_response = ""
        iterations = 0

        try:
            while iterations < self.max_iterations:
                iterations += 1
                log.debug(f"Agent iteration {iterations}")

                # ── Think ─────────────────────────────────────────────────
                accumulated_text = ""
                tool_calls_received: list[ToolCall] = []

                async for chunk in self.backend.stream_chat(
                    messages=self.history.get_messages(),
                    tools=self.tools_manifest if self.tools_manifest else None,
                ):
                    if isinstance(chunk, str):
                        accumulated_text += chunk
                        yield TextChunkEvent(chunk)
                    elif isinstance(chunk, ToolCall):
                        tool_calls_received.append(chunk)

                # If no tool calls streamed, do a non-streaming call to get them
                if not tool_calls_received and accumulated_text:
                    # Check if response already complete (no tool calls needed)
                    final_response = accumulated_text
                    self.history.add_assistant(accumulated_text)
                    break

                if tool_calls_received:
                    # Record assistant message with tool calls
                    tc_dicts = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
                        }
                        for tc in tool_calls_received
                    ]
                    self.history.add_assistant(accumulated_text, tool_calls=tc_dicts)

                    # ── Act ───────────────────────────────────────────────
                    for tc in tool_calls_received:
                        yield ToolCallEvent(tool_name=tc.name, arguments=tc.arguments, call_id=tc.id)

                        # Confirmation gate for dangerous tools
                        if self.require_confirm and tc.name in DANGEROUS_TOOLS:
                            cmd_preview = self._format_cmd_preview(tc.name, tc.arguments)
                            confirm_evt = ConfirmationRequiredEvent(
                                tool_name=tc.name,
                                command=cmd_preview,
                                call_id=tc.id,
                            )
                            yield confirm_evt
                            # Wait for GUI to set the confirm_event
                            await confirm_evt.confirm_event.wait()
                            if not confirm_evt.confirmed:
                                self.history.add_tool_result(tc.id, tc.name, "User cancelled execution.")
                                yield ToolResultEvent(tc.name, tc.id, "User cancelled execution.", error=True)
                                continue

                        # Execute tool
                        try:
                            result = await asyncio.get_event_loop().run_in_executor(
                                None, lambda n=tc.name, a=tc.arguments: self.tool_executor(n, a)
                            )
                            output = str(result)
                        except Exception as e:
                            output = f"Tool error: {e}"
                            yield ToolResultEvent(tc.name, tc.id, output, error=True)
                            self.history.add_tool_result(tc.id, tc.name, output)
                            continue

                        yield ToolResultEvent(tc.name, tc.id, output)
                        self.history.add_tool_result(tc.id, tc.name, output)

                else:
                    # No tool calls — we're done
                    final_response = accumulated_text
                    break

            else:
                # Max iterations reached
                msg = f"\n\n*[Agent reached max iterations ({self.max_iterations})]*"
                yield TextChunkEvent(msg)
                final_response += msg

        except Exception as e:
            log.exception("Agent error")
            yield AgentErrorEvent(str(e))
            return

        yield AgentDoneEvent(final_response=final_response, iterations=iterations)

    def _format_cmd_preview(self, tool_name: str, args: dict) -> str:
        """Format a human-readable command preview for confirmation."""
        arg_str = " ".join(f"{k}={v!r}" for k, v in args.items())
        return f"{tool_name}({arg_str})"
