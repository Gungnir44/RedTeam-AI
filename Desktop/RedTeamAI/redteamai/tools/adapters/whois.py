"""Whois tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.utils.platform_utils import smart_wrap
from redteamai.ai.tool_manifest import build_tool_schema, string_param


class WhoisTool(BaseTool):
    def __init__(self, binary: str = "whois"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "whois"

    @property
    def display_name(self) -> str:
        return "Whois"

    @property
    def description(self) -> str:
        return "Domain and IP registration lookup"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "target": string_param("Domain name or IP address to look up"),
                "server": string_param("Optional WHOIS server to query"),
            },
            required=["target"],
        )

    def execute(self, target: str, server: str = "", **_) -> ToolResult:
        target = sanitize_target(target)
        cmd = [self._binary]
        if server:
            cmd.extend(["-h", sanitize_target(server)])
        cmd.append(target)
        return run_command(smart_wrap(self._binary, cmd), timeout=30)
