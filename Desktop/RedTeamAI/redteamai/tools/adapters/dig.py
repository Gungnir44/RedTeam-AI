"""Dig (DNS lookup) tool adapter."""
from __future__ import annotations
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.tools.executor import run_command
from redteamai.utils.sanitizer import sanitize_target
from redteamai.ai.tool_manifest import build_tool_schema, string_param


class DigTool(BaseTool):
    def __init__(self, binary: str = "dig"):
        self._binary = binary

    @property
    def name(self) -> str:
        return "dig"

    @property
    def display_name(self) -> str:
        return "Dig (DNS)"

    @property
    def description(self) -> str:
        return "DNS lookup tool — query A, MX, NS, TXT, CNAME, SOA, ANY records"

    @property
    def binary(self) -> str:
        return self._binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "target": string_param("Domain name or IP to query"),
                "record_type": string_param("DNS record type", enum=["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "ANY", "PTR", "SRV"]),
                "nameserver": string_param("Optional nameserver to query (e.g. 8.8.8.8)"),
                "axfr": string_param("Attempt zone transfer for this domain"),
            },
            required=["target"],
        )

    def execute(self, target: str, record_type: str = "A", nameserver: str = "", axfr: str = "", **_) -> ToolResult:
        target = sanitize_target(target)
        if axfr:
            # Zone transfer
            cmd = [self._binary, f"@{sanitize_target(nameserver) if nameserver else target}", sanitize_target(axfr), "AXFR"]
        else:
            cmd = [self._binary]
            if nameserver:
                cmd.append(f"@{sanitize_target(nameserver)}")
            cmd.extend([target, record_type or "A"])
        return run_command(cmd, timeout=30)
