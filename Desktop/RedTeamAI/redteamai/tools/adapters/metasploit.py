"""Metasploit RPC adapter (requires msfrpcd running)."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.utils.sanitizer import sanitize_arg
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param


class MetasploitTool(BaseTool):
    def __init__(self, host: str = "127.0.0.1", port: int = 55553, password: str = ""):
        self._host = host
        self._port = port
        self._password = password

    @property
    def name(self) -> str:
        return "metasploit_exec"

    @property
    def display_name(self) -> str:
        return "Metasploit"

    @property
    def description(self) -> str:
        return "Execute Metasploit Framework commands via RPC (requires msfrpcd)"

    @property
    def is_dangerous(self) -> bool:
        return True

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "command": string_param("MSF console command (e.g. 'use exploit/multi/handler')"),
                "module": string_param("MSF module path (e.g. 'exploit/windows/smb/ms17_010_eternalblue')"),
                "options": string_param("Module options as KEY=VALUE pairs (e.g. 'RHOSTS=192.168.1.1 LPORT=4444')"),
            },
            required=["command"],
        )

    def execute(self, command: str, module: str = "", options: str = "", **_) -> ToolResult:
        """Execute via MSF RPC if available, otherwise return guidance."""
        try:
            import msgpack  # type: ignore
            return self._rpc_execute(command, module, options)
        except ImportError:
            return ToolResult(
                success=False,
                output="",
                error="Metasploit RPC requires 'msgpack' package and msfrpcd running.\n"
                      "Start RPC: msfrpcd -P <password> -S\n"
                      "Install msgpack: pip install msgpack",
            )

    def _rpc_execute(self, command: str, module: str, options: str) -> ToolResult:
        """Actual RPC call — only reached if msgpack available."""
        return ToolResult(
            success=False,
            output="",
            error="Metasploit RPC execution not yet implemented. Use msfconsole manually.",
        )
