"""SearchSploit (ExploitDB) adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_arg
from redteamai.ai.tool_manifest import build_tool_schema, string_param, boolean_param


class SearchsploitTool(BaseTool):
    def __init__(self, binary: str = "searchsploit"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "searchsploit"

    @property
    def display_name(self) -> str:
        return "SearchSploit"

    @property
    def description(self) -> str:
        return "Search ExploitDB for public exploits by software name/version"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "query": string_param("Search query (e.g. 'Apache 2.4.49', 'WordPress 5.8')"),
                "exact": boolean_param("Exact match only"),
                "cve": string_param("Search by CVE ID (e.g. CVE-2021-41773)"),
            },
            required=["query"],
        )

    def execute(self, query: str, exact: bool = False, cve: str = "", **_) -> ToolResult:
        cmd = [self._binary, "--colour"]
        if cve:
            cmd.extend(["--cve", sanitize_arg(cve)])
        elif exact:
            cmd.extend(["-e", sanitize_arg(query)])
        else:
            cmd.append(sanitize_arg(query))
        return run_command(cmd, timeout=30)
