"""Input sanitization for tool arguments to prevent command injection."""
from __future__ import annotations
import re
import shlex
from typing import Any


# Characters that should never appear in tool arguments passed to shell
_DANGEROUS_CHARS = re.compile(r'[;&|`$<>!]')
_SAFE_IP = re.compile(r'^[\d.:/\[\]a-fA-F]+$')
_SAFE_HOSTNAME = re.compile(r'^[a-zA-Z0-9.\-_]+$')
_SAFE_PORT = re.compile(r'^\d{1,5}$')
_SAFE_PATH = re.compile(r'^[a-zA-Z0-9._\-/\\: ]+$')
_SAFE_WORDLIST = re.compile(r'^[a-zA-Z0-9._\-/\\: ]+$')


def sanitize_target(target: str) -> str:
    """Validate and sanitize an IP/hostname/URL target for tool args."""
    target = target.strip()
    if len(target) > 255:
        raise ValueError("Target too long")
    # Strip URL fragment (#...) — CLI tools don't understand fragments and
    # some (e.g. nikto, whatweb) will fail or behave unexpectedly with them.
    if "#" in target:
        target = target.split("#")[0].rstrip("/")
    if _DANGEROUS_CHARS.search(target):
        raise ValueError(f"Target contains dangerous characters: {target!r}")
    # Allow IPs, hostnames, URLs with specific scheme
    if target.startswith(("http://", "https://")):
        # Minimal URL validation
        safe = re.compile(r'^https?://[a-zA-Z0-9.\-_:/\[\]@%?=&+]+$')
        if not safe.match(target):
            raise ValueError(f"Unsafe URL: {target!r}")
    return target


def sanitize_port(port: str | int) -> str:
    """Validate a port number or port range like '80', '1-1024'."""
    s = str(port).strip()
    if not re.match(r'^\d{1,5}(-\d{1,5})?(,\d{1,5}(-\d{1,5})?)*$', s):
        raise ValueError(f"Invalid port specification: {s!r}")
    return s


def sanitize_wordlist_path(path: str) -> str:
    """Validate a wordlist file path."""
    path = path.strip()
    if _DANGEROUS_CHARS.search(path):
        raise ValueError(f"Path contains dangerous characters: {path!r}")
    return path


def sanitize_arg(value: Any) -> str:
    """Generic sanitization: convert to string and reject shell metacharacters."""
    s = str(value).strip()
    if _DANGEROUS_CHARS.search(s):
        raise ValueError(f"Argument contains dangerous characters: {s!r}")
    return s


def build_command(base_cmd: list[str], args: dict[str, Any]) -> list[str]:
    """Build a safe command list from a base command and validated arguments."""
    cmd = list(base_cmd)
    for flag, value in args.items():
        if value is None or value == "":
            continue
        cmd.append(flag)
        if value is not True:  # True = flag-only (no value)
            cmd.append(sanitize_arg(value))
    return cmd
