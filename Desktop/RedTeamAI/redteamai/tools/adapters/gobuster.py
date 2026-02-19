"""Gobuster tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target, sanitize_wordlist_path
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param, boolean_param


class GobusterTool(BaseTool):
    def __init__(self, binary: str = "gobuster"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "gobuster"

    @property
    def display_name(self) -> str:
        return "Gobuster"

    @property
    def description(self) -> str:
        return "Directory/file brute-force and subdomain enumeration (web)"

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
                "url": string_param("Target URL (e.g. http://example.com)"),
                "wordlist": string_param("Path to wordlist file"),
                "mode": string_param("Mode", enum=["dir", "dns", "vhost"]),
                "extensions": string_param("File extensions to check (e.g. 'php,html,txt')"),
                "threads": integer_param("Number of concurrent threads", minimum=1, maximum=50),
                "status_codes": string_param("Status codes to show (e.g. '200,301,302')"),
            },
            required=["url", "wordlist"],
        )

    def get_command(self, url: str, wordlist: str, mode: str = "dir",
                    extensions: str = "", threads: int = 10, status_codes: str = "200,301,302,307", **_) -> list[str]:
        url = sanitize_target(url)
        wordlist = sanitize_wordlist_path(wordlist)
        cmd = [self._binary, mode, "-u", url, "-w", wordlist, "-t", str(threads), "--no-error"]
        if extensions and mode == "dir":
            cmd.extend(["-x", extensions])
        if status_codes:
            cmd.extend(["-s", status_codes])
        return cmd

    def execute(self, url: str, wordlist: str, mode: str = "dir",
                extensions: str = "", threads: int = 10, status_codes: str = "200,301,302,307", **_) -> ToolResult:
        return run_command(self.get_command(url=url, wordlist=wordlist, mode=mode,
                                            extensions=extensions, threads=threads,
                                            status_codes=status_codes), timeout=300)
