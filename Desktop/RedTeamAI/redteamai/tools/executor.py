"""Synchronous subprocess executor used by QThread and direct calls."""
from __future__ import annotations
import sys
import subprocess
import time
from redteamai.tools.base import ToolResult
from redteamai.utils.logger import get_logger

log = get_logger(__name__)

_HIDE_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def run_command(
    command: list[str],
    timeout: int = 120,
    cwd: str | None = None,
    env: dict | None = None,
) -> ToolResult:
    """Run a command synchronously and return a ToolResult."""
    log.debug(f"Executing: {' '.join(command)}")
    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=cwd,
            env=env,
            creationflags=_HIDE_WINDOW,
        )
        elapsed = time.monotonic() - start
        output = result.stdout or ""
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return ToolResult(
            success=result.returncode == 0,
            output=output.strip(),
            exit_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, output="", error=f"Command timed out after {timeout}s", exit_code=124)
    except FileNotFoundError:
        return ToolResult(success=False, output="", error=f"Binary not found: {command[0]}", exit_code=127)
    except OSError as e:
        return ToolResult(success=False, output="", error=str(e), exit_code=1)
