"""QThread that runs subprocess tools with live output streaming."""
from __future__ import annotations
import sys
import subprocess
import time
from PyQt6.QtCore import QThread
from redteamai.workers.worker_signals import ToolWorkerSignals
from redteamai.utils.logger import get_logger

log = get_logger(__name__)

_HIDE_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


class ToolWorker(QThread):
    """
    Runs an external tool as a subprocess, streaming stdout+stderr
    line-by-line via signals for real-time terminal output.
    """

    def __init__(self, command: list[str], cwd: str | None = None, timeout: int = 300, parent=None):
        super().__init__(parent)
        self.command = command
        self.cwd = cwd
        self.timeout = timeout
        self.signals = ToolWorkerSignals()
        self._process: subprocess.Popen | None = None
        self._output_lines: list[str] = []

    def run(self) -> None:
        start = time.monotonic()
        try:
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=self.cwd,
                bufsize=1,  # Line-buffered
                creationflags=_HIDE_WINDOW,
            )
        except FileNotFoundError as e:
            msg = f"[Error] Tool not found: {self.command[0]}\n{e}"
            self.signals.output_line.emit(msg)
            self.signals.finished.emit(127, msg)
            return
        except OSError as e:
            msg = f"[Error] Failed to launch tool: {e}"
            self.signals.output_line.emit(msg)
            self.signals.finished.emit(1, msg)
            return

        try:
            for line in iter(self._process.stdout.readline, ""):
                if not self.isRunning():
                    break
                self._output_lines.append(line)
                self.signals.output_line.emit(line.rstrip("\n"))

                # Timeout check
                if time.monotonic() - start > self.timeout:
                    self._process.kill()
                    self.signals.output_line.emit(f"\n[Timeout after {self.timeout}s — process killed]")
                    break

            self._process.wait(timeout=10)
        except Exception as e:
            log.exception("ToolWorker error")
            self.signals.output_line.emit(f"[Error] {e}")

        exit_code = self._process.returncode if self._process.returncode is not None else -1
        full_output = "".join(self._output_lines)
        self.signals.finished.emit(exit_code, full_output)

    def stop(self) -> None:
        """Kill the subprocess and stop the thread."""
        if self._process and self._process.poll() is None:
            self._process.kill()
        self.wait(3000)
