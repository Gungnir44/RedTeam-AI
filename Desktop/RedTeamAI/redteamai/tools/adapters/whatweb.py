"""WhatWeb technology fingerprinting adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.ai.tool_manifest import build_tool_schema, string_param


class WhatwebTool(BaseTool):
    def __init__(self, binary: str = "whatweb"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "whatweb"

    @property
    def display_name(self) -> str:
        return "WhatWeb"

    @property
    def description(self) -> str:
        return "Web technology fingerprinting — CMS, frameworks, server info, versions"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "target": string_param("Target URL or IP"),
                "aggression": string_param("Aggression level", enum=["1", "3", "4"]),
            },
            required=["target"],
        )

    def execute(self, target: str, aggression: str = "1", **_) -> ToolResult:
        target = sanitize_target(target)
        cmd = [self._binary, target, f"-a{aggression}", "--color=never"]
        return run_command(cmd, timeout=60)
