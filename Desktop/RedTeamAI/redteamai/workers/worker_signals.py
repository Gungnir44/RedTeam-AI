"""PyQt6 signals for worker threads."""
from __future__ import annotations
from PyQt6.QtCore import QObject, pyqtSignal


class AIWorkerSignals(QObject):
    """Signals emitted by AIWorker."""
    text_chunk = pyqtSignal(str)           # Streaming text token
    tool_call = pyqtSignal(str, dict)      # (tool_name, arguments)
    tool_result = pyqtSignal(str, str, bool)  # (tool_name, output, is_error)
    confirm_required = pyqtSignal(object)  # ConfirmationRequiredEvent
    done = pyqtSignal(str, int)            # (final_response, iterations)
    error = pyqtSignal(str)               # Error message


class ToolWorkerSignals(QObject):
    """Signals emitted by ToolWorker."""
    output_line = pyqtSignal(str)          # One line of stdout/stderr
    finished = pyqtSignal(int, str)        # (exit_code, full_output)
    error = pyqtSignal(str)               # Subprocess launch error
    progress = pyqtSignal(int)            # Estimated progress 0-100 (optional)
