"""ToolRegistry: discover, check availability, expose manifest."""
from __future__ import annotations
from typing import Any
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.utils.platform_utils import probe_tool
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


class ToolRegistry:
    """Central registry for all tools."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._availability: dict[str, tuple[bool, str]] = {}  # name -> (available, hint)

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def probe_all(self) -> None:
        """Check availability of all registered tools."""
        for name, tool in self._tools.items():
            if tool.is_builtin:
                self._availability[name] = (True, "Built-in")
            elif tool.binary:
                available, hint = probe_tool(tool.binary)
                self._availability[name] = (available, hint)
            else:
                self._availability[name] = (True, "")

    def is_available(self, name: str) -> bool:
        status = self._availability.get(name)
        if status is None:
            return False
        return status[0]

    def get_hint(self, name: str) -> str:
        status = self._availability.get(name)
        if status is None:
            return "Tool not registered"
        return status[1]

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_manifest(self) -> list[dict]:
        """Return OpenAI-compatible tool schemas for available tools."""
        return [
            tool.get_schema()
            for name, tool in self._tools.items()
            if self.is_available(name)
        ]

    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(success=False, output="", error=f"Unknown tool: {name}")
        if not self.is_available(name):
            hint = self.get_hint(name)
            return ToolResult(success=False, output="", error=f"Tool '{name}' not available. {hint}")
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            log.exception(f"Tool {name} raised exception")
            return ToolResult(success=False, output="", error=str(e))

    def execute_from_ai(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Called by the AI agent — returns string output."""
        result = self.execute(tool_name, **arguments)
        if result.success or result.output:
            return result.output or result.error
        return f"[Error] {result.error}"

    def list_tools(self) -> list[dict]:
        """List all tools with availability info."""
        return [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "available": self.is_available(t.name),
                "hint": self.get_hint(t.name),
                "is_dangerous": t.is_dangerous,
                "is_builtin": t.is_builtin,
            }
            for t in self._tools.values()
        ]


def build_default_registry(settings=None) -> ToolRegistry:
    """Build and return the default registry with all tools registered."""
    from redteamai.tools.adapters.builtin_ctf import BuiltinCTFTool
    from redteamai.tools.adapters.nmap import NmapTool
    from redteamai.tools.adapters.whois import WhoisTool
    from redteamai.tools.adapters.dig import DigTool
    from redteamai.tools.adapters.theharvester import TheHarvesterTool
    from redteamai.tools.adapters.subfinder import SubfinderTool
    from redteamai.tools.adapters.gobuster import GobusterTool
    from redteamai.tools.adapters.ffuf import FfufTool
    from redteamai.tools.adapters.nikto import NiktoTool
    from redteamai.tools.adapters.whatweb import WhatwebTool
    from redteamai.tools.adapters.searchsploit import SearchsploitTool
    from redteamai.tools.adapters.cve_lookup import CVELookupTool

    registry = ToolRegistry()
    tool_paths = settings.tools if settings else None

    def _binary(name: str) -> str:
        if tool_paths:
            return getattr(tool_paths, name, name)
        return name

    registry.register(BuiltinCTFTool())
    registry.register(NmapTool(_binary("nmap")))
    registry.register(WhoisTool(_binary("whois")))
    registry.register(DigTool(_binary("dig")))
    registry.register(TheHarvesterTool(_binary("theharvester")))
    registry.register(SubfinderTool(_binary("subfinder")))
    registry.register(GobusterTool(_binary("gobuster")))
    registry.register(FfufTool(_binary("ffuf")))
    registry.register(NiktoTool(_binary("nikto")))
    registry.register(WhatwebTool(_binary("whatweb")))
    registry.register(SearchsploitTool(_binary("searchsploit")))
    registry.register(CVELookupTool())

    registry.probe_all()
    return registry
