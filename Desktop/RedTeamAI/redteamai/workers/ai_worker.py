"""QThread that runs the asyncio ReAct agent loop."""
from __future__ import annotations
import asyncio
import nest_asyncio
from PyQt6.QtCore import QThread
from redteamai.ai.agent import (
    RedTeamAgent, TextChunkEvent, ToolCallEvent, ToolResultEvent,
    ConfirmationRequiredEvent, AgentDoneEvent, AgentErrorEvent
)
from redteamai.workers.worker_signals import AIWorkerSignals
from redteamai.utils.logger import get_logger

log = get_logger(__name__)
nest_asyncio.apply()


class AIWorker(QThread):
    """
    Runs the RedTeamAgent ReAct loop in a dedicated thread with its own
    asyncio event loop. Communicates back to Qt via AIWorkerSignals.
    """

    def __init__(self, agent: RedTeamAgent, user_message: str, parent=None):
        super().__init__(parent)
        self.agent = agent
        self.user_message = user_message
        self.signals = AIWorkerSignals()
        self._loop: asyncio.AbstractEventLoop | None = None

    def run(self) -> None:
        """QThread entry point — runs asyncio loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run_agent())
        except Exception as e:
            log.exception("AIWorker crashed")
            self.signals.error.emit(str(e))
        finally:
            self._loop.close()

    async def _run_agent(self) -> None:
        async for event in self.agent.run(self.user_message):
            if isinstance(event, TextChunkEvent):
                self.signals.text_chunk.emit(event.text)

            elif isinstance(event, ToolCallEvent):
                self.signals.tool_call.emit(event.tool_name, event.arguments)

            elif isinstance(event, ToolResultEvent):
                self.signals.tool_result.emit(event.tool_name, event.output, event.error)

            elif isinstance(event, ConfirmationRequiredEvent):
                self.signals.confirm_required.emit(event)
                # Wait for GUI to resolve — the event.confirm_event is set by GUI
                await event.confirm_event.wait()

            elif isinstance(event, AgentDoneEvent):
                self.signals.done.emit(event.final_response, event.iterations)

            elif isinstance(event, AgentErrorEvent):
                self.signals.error.emit(event.error)

    def stop(self) -> None:
        """Request the worker to stop."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        self.wait(3000)
