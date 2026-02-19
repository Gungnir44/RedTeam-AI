"""Nikto web vulnerability scanner adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param, boolean_param


class NiktoTool(BaseTool):
    def __init__(self, binary: str = "nikto"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "nikto"

    @property
    def display_name(self) -> str:
        return "Nikto"

    @property
    def description(self) -> str:
        return "Web server vulnerability scanner — misconfigs, outdated software, dangerous files"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "target": string_param("Target URL or IP:port (e.g. http://example.com or 192.168.1.1:8080)"),
                "port": string_param("Port number (if not in URL)"),
                "ssl": boolean_param("Use SSL/TLS"),
                "timeout": integer_param("Timeout in seconds", minimum=30, maximum=600),
            },
            required=["target"],
        )

    def execute(self, target: str, port: str = "", ssl: bool = False, timeout: int = 120, **_) -> ToolResult:
        target = sanitize_target(target)
        cmd = [self._binary, "-h", target, "-nointeractive"]
        if port:
            cmd.extend(["-p", port])
        if ssl:
            cmd.append("-ssl")
        return run_command(cmd, timeout=timeout)
