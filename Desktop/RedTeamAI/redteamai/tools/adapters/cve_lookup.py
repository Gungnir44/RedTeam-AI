"""CVE lookup via NVD API (free, no key required for basic rate limit)."""
from __future__ import annotations
import httpx
from redteamai.tools.base import BaseTool, ToolResult
from redteamai.utils.sanitizer import sanitize_arg
from redteamai.ai.tool_manifest import build_tool_schema, string_param, integer_param

NVD_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class CVELookupTool(BaseTool):
    def __init__(self, api_key: str = ""):
        self._api_key = api_key

    @property
    def name(self) -> str:
        return "cve_lookup"

    @property
    def display_name(self) -> str:
        return "CVE Lookup"

    @property
    def description(self) -> str:
        return "Look up CVE details from NVD (NIST National Vulnerability Database)"

    @property
    def is_builtin(self) -> bool:
        return True  # Pure Python/HTTP, no binary

    def get_schema(self) -> dict:
        return build_tool_schema(
            name=self.name,
            description=self.description,
            parameters={
                "cve_id": string_param("CVE ID to look up (e.g. CVE-2021-44228)"),
                "keyword": string_param("Keyword search for vulnerabilities (alternative to cve_id)"),
                "max_results": integer_param("Maximum results to return", minimum=1, maximum=20),
            },
        )

    def execute(self, cve_id: str = "", keyword: str = "", max_results: int = 5, **_) -> ToolResult:
        try:
            return self._lookup(cve_id, keyword, max_results)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def _lookup(self, cve_id: str, keyword: str, max_results: int) -> ToolResult:
        params: dict = {"resultsPerPage": max_results}
        if cve_id:
            params["cveId"] = sanitize_arg(cve_id)
        elif keyword:
            params["keywordSearch"] = sanitize_arg(keyword)
        else:
            return ToolResult(success=False, output="", error="Provide either cve_id or keyword")

        headers = {}
        if self._api_key:
            headers["apiKey"] = self._api_key

        with httpx.Client(timeout=30) as client:
            r = client.get(NVD_BASE, params=params, headers=headers)
            r.raise_for_status()
            data = r.json()

        vulns = data.get("vulnerabilities", [])
        if not vulns:
            return ToolResult(success=True, output="No CVEs found matching the query.")

        lines = []
        for item in vulns:
            cve = item.get("cve", {})
            cve_id_val = cve.get("id", "N/A")
            desc_list = cve.get("descriptions", [])
            desc = next((d["value"] for d in desc_list if d.get("lang") == "en"), "No description")
            metrics = cve.get("metrics", {})
            score = "N/A"
            severity = "N/A"
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                if key in metrics and metrics[key]:
                    m = metrics[key][0]
                    score = m.get("cvssData", {}).get("baseScore", "N/A")
                    severity = m.get("cvssData", {}).get("baseSeverity", "N/A")
                    break

            lines.append(f"**{cve_id_val}** | CVSS: {score} ({severity})")
            lines.append(f"  {desc[:300]}")
            lines.append("")

        return ToolResult(success=True, output="\n".join(lines))
