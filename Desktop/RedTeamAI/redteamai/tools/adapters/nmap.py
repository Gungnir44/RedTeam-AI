"""Nmap tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target, sanitize_port
from redteamai.ai.tool_manifest import build_tool_schema, string_param, boolean_param, integer_param


class NmapTool(BaseTool):
    def __init__(self, binary: str = "nmap"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "nmap"

    @property
    def display_name(self) -> str:
        return "Nmap"

    @property
    def description(self) -> str:
        return "Network port scanner and service/OS detection"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "target": string_param("Target IP, hostname, or CIDR range (e.g. 192.168.1.0/24)"),
                "ports": string_param("Ports to scan (e.g. '80,443', '1-1024', '-' for all). Default: top 1000"),
                "scan_type": string_param("Scan type", enum=["sV", "sS", "sT", "sA", "sU", "sn", "A", "O"]),
                "timing": string_param("Timing template", enum=["T0", "T1", "T2", "T3", "T4", "T5"]),
                "extra_args": string_param("Additional nmap flags (e.g. '--script vuln')"),
                "timeout": integer_param("Timeout in seconds", minimum=5, maximum=600),
            },
            required=["target"],
        )

    def get_command(self, target: str, ports: str = "", scan_type: str = "sV",
                    timing: str = "T4", extra_args: str = "", **_) -> list[str]:
        target = sanitize_target(target)
        cmd = [self._binary, f"-{scan_type}", f"-{timing}", "--open"]
        if ports:
            cmd.extend(["-p", sanitize_port(ports)])
        if extra_args:
            # Split safely — extra_args is for trusted pentesters
            import shlex
            cmd.extend(shlex.split(extra_args))
        cmd.append(target)
        return cmd

    def execute(self, target: str, ports: str = "", scan_type: str = "sV",
                timing: str = "T4", extra_args: str = "", timeout: int = 120, **_) -> ToolResult:
        cmd = self.get_command(target, ports, scan_type, timing, extra_args)
        return run_command(cmd, timeout=timeout)
