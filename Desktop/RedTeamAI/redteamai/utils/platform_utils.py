"""OS detection, WSL bridge, tool availability probing."""
from __future__ import annotations
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from functools import lru_cache
from redteamai.utils.logger import get_logger

log = get_logger(__name__)

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform == "linux"
IS_MAC = sys.platform == "darwin"

# Suppress console window flashes on Windows for all subprocess calls
_HIDE_WINDOW = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0


@lru_cache(maxsize=None)
def has_wsl() -> bool:
    """Check if WSL is available on Windows."""
    if not IS_WINDOWS:
        return False
    try:
        r = subprocess.run(["wsl", "--status"], capture_output=True, timeout=5,
                           creationflags=_HIDE_WINDOW)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def probe_tool(binary: str, version_flag: str = "--version") -> tuple[bool, str]:
    """
    Check if a binary exists and return (available, hint).
    Returns install hint if not found.
    """
    # Check direct path
    if shutil.which(binary):
        try:
            r = subprocess.run([binary, version_flag], capture_output=True, timeout=5,
                               text=True, creationflags=_HIDE_WINDOW)
            ver = (r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else ""
            return True, ver[:80]
        except Exception:
            return True, ""

    # Try WSL wrapper on Windows
    if IS_WINDOWS and has_wsl():
        try:
            r = subprocess.run(["wsl", binary, version_flag], capture_output=True, timeout=5,
                               text=True, creationflags=_HIDE_WINDOW)
            if r.returncode == 0:
                ver = (r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else ""
                return True, f"[WSL] {ver[:70]}"
        except Exception:
            pass

    return False, _install_hint(binary)


def _install_hint(binary: str) -> str:
    hints = {
        "nmap": "Install: https://nmap.org/download  (Windows: choco install nmap  |  Linux: apt install nmap)",
        "whois": "Install: choco install whois  |  apt install whois",
        "dig": "Install: choco install bind-toolsonly  |  apt install dnsutils",
        "gobuster": "Install: https://github.com/OJ/gobuster/releases",
        "ffuf": "Install: https://github.com/ffuf/ffuf/releases",
        "nikto": "Install: https://github.com/sullo/nikto  |  apt install nikto",
        "whatweb": "Install: apt install whatweb  |  gem install whatweb",
        "theHarvester": "Install: pip install theHarvester  |  apt install theharvester",
        "subfinder": "Install: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "searchsploit": "Install: apt install exploitdb  (Kali/Ubuntu)",
        "msfconsole": "Install: https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html",
    }
    return hints.get(binary, f"'{binary}' not found in PATH. Please install it.")


def wsl_wrap(cmd: list[str]) -> list[str]:
    """Wrap a command list with 'wsl' prefix for Windows."""
    if IS_WINDOWS and has_wsl():
        return ["wsl"] + cmd
    return cmd


def get_platform_info() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python": platform.python_version(),
        "arch": platform.machine(),
        "is_windows": IS_WINDOWS,
        "is_linux": IS_LINUX,
        "has_wsl": has_wsl() if IS_WINDOWS else False,
    }
