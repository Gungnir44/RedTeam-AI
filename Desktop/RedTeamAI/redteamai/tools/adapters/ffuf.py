"""ffuf (Fuzz Faster U Fool) tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target, sanitize_wordlist_path
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param


class FfufTool(BaseTool):
    def __init__(self, binary: str = "ffuf"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "ffuf"

    @property
    def display_name(self) -> str:
        return "ffuf"

    @property
    def description(self) -> str:
        return "Web fuzzer for directories, parameters, headers, and virtual hosts"

    @property
    def binary(self) -> str:
        return self._binary

    @property
    def is_dangerous(self) -> bool:
        return True

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "url": string_param("Target URL with FUZZ placeholder (e.g. http://example.com/FUZZ)"),
                "wordlist": string_param("Path to wordlist file"),
                "extensions": string_param("Extensions to append (e.g. '.php,.html')"),
                "filter_code": string_param("Filter response codes (e.g. '404,403')"),
                "threads": integer_param("Concurrent threads", minimum=1, maximum=50),
                "timeout": integer_param("Request timeout seconds", minimum=5, maximum=60),
            },
            required=["url", "wordlist"],
        )

    def execute(self, url: str, wordlist: str, extensions: str = "",
                filter_code: str = "404", threads: int = 40, timeout: int = 10, **_) -> ToolResult:
        url = sanitize_target(url)
        wordlist = sanitize_wordlist_path(wordlist)
        cmd = [self._binary, "-u", url, "-w", wordlist, "-t", str(threads),
               "-timeout", str(timeout), "-noninteractive"]
        if extensions:
            cmd.extend(["-e", extensions])
        if filter_code:
            cmd.extend(["-fc", filter_code])
        return run_command(cmd, timeout=300)
