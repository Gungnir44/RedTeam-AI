"""theHarvester tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param


class TheHarvesterTool(BaseTool):
    def __init__(self, binary: str = "theHarvester"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "theharvester"

    @property
    def display_name(self) -> str:
        return "theHarvester"

    @property
    def description(self) -> str:
        return "Email, subdomain, and OSINT harvesting from public sources"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "domain": string_param("Target domain to harvest"),
                "sources": string_param("Data sources (e.g. 'google,bing,dnsdumpster'). Default: all"),
                "limit": integer_param("Maximum results per source", minimum=10, maximum=500),
            },
            required=["domain"],
        )

    def execute(self, domain: str, sources: str = "all", limit: int = 100, **_) -> ToolResult:
        domain = sanitize_target(domain)
        cmd = [self._binary, "-d", domain, "-b", sources, "-l", str(limit)]
        return run_command(cmd, timeout=120)
