"""Report generation dispatcher."""
from __future__ import annotations
from pathlib import Path


def generate_report(findings: list[dict], fmt: str, output_path: str) -> None:
    """Generate a report in the specified format."""
    path = Path(output_path)
    if fmt == "md":
        from redteamai.reporting.markdown_export import export_markdown
        content = export_markdown(findings)
        path.write_text(content, encoding="utf-8")
    elif fmt == "html":
        from redteamai.reporting.markdown_export import export_markdown
        import re
        md = export_markdown(findings)
        # Simple MD to HTML
        html = _md_to_html(md)
        path.write_text(html, encoding="utf-8")
    elif fmt == "pdf":
        from redteamai.reporting.pdf_export import export_pdf
        export_pdf(findings, path)
    else:
        raise ValueError(f"Unknown report format: {fmt}")


def _md_to_html(md: str) -> str:
    """Very simple Markdown to HTML for report export."""
    import re
    lines = []
    for line in md.split("\n"):
        if line.startswith("# "):
            line = f"<h1>{line[2:]}</h1>"
        elif line.startswith("## "):
            line = f"<h2>{line[3:]}</h2>"
        elif line.startswith("### "):
            line = f"<h3>{line[4:]}</h3>"
        elif line.startswith("- "):
            line = f"<li>{line[2:]}</li>"
        elif line.startswith("**") and line.endswith("**"):
            line = f"<strong>{line[2:-2]}</strong>"
        else:
            line = f"<p>{line}</p>" if line.strip() else ""
        lines.append(line)

    body = "\n".join(lines)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>RedTeam AI Report</title>
<style>
body {{ font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; padding: 40px; max-width: 900px; margin: auto; }}
h1 {{ color: #f85149; }} h2 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 4px; }}
h3 {{ color: #d29922; }} code {{ background: #21262d; padding: 2px 6px; border-radius: 3px; }}
.critical {{ color: #ff4444; }} .high {{ color: #f85149; }} .medium {{ color: #d29922; }} .low {{ color: #3fb950; }} .info {{ color: #58a6ff; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
