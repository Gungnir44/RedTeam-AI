"""Subfinder tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.utils.platform_utils import smart_wrap
from redteamai.ai.tool_manifest import build_tool_schema, string_param, boolean_param


class SubfinderTool(BaseTool):
    def __init__(self, binary: str = "subfinder"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "subfinder"

    @property
    def display_name(self) -> str:
        return "Subfinder"

    @property
    def description(self) -> str:
        return "Passive subdomain enumeration using multiple sources"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "domain": string_param("Target domain for subdomain discovery"),
                "silent": boolean_param("Only output subdomains, no banner"),
                "recursive": boolean_param("Recursively find subdomains"),
            },
            required=["domain"],
        )

    def execute(self, domain: str, silent: bool = True, recursive: bool = False, **_) -> ToolResult:
        domain = sanitize_target(domain)
        cmd = [self._binary, "-d", domain]
        if silent:
            cmd.append("-silent")
        if recursive:
            cmd.append("-recursive")
        return run_command(smart_wrap(self._binary, cmd), timeout=120)
