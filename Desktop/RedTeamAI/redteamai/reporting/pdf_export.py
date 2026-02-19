"""PDF report export using reportlab (no GTK/wkhtmltopdf required)."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime


def export_pdf(findings: list[dict], output_path: Path) -> None:
    """Generate a PDF report using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import cm
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    # Dark theme colors approximated for print
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                  textColor=HexColor("#c9d1d9"), fontSize=24, spaceAfter=12)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                               textColor=HexColor("#58a6ff"), fontSize=14, spaceBefore=12, spaceAfter=6)
    h3_style = ParagraphStyle("H3", parent=styles["Heading3"],
                               textColor=HexColor("#d29922"), fontSize=12, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body2", parent=styles["Normal"],
                                 textColor=HexColor("#c9d1d9"), fontSize=10, spaceAfter=6)

    sev_colors = {
        "critical": HexColor("#ff4444"), "high": HexColor("#f85149"),
        "medium": HexColor("#d29922"), "low": HexColor("#3fb950"), "info": HexColor("#58a6ff"),
    }

    story = []
    story.append(Paragraph("Penetration Test Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(HRFlowable(width="100%", color=HexColor("#30363d")))
    story.append(Spacer(1, 0.5*cm))

    # Summary table
    story.append(Paragraph("Executive Summary", h2_style))
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev = f.get("severity", "info").lower()
        counts[sev] = counts.get(sev, 0) + 1

    table_data = [["Severity", "Count"]] + [[sev.title(), str(cnt)] for sev, cnt in counts.items()]
    t = Table(table_data, colWidths=[4*cm, 2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#21262d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#c9d1d9")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#30363d")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#161b22"), HexColor("#1c2128")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), HexColor("#c9d1d9")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Findings
    story.append(Paragraph("Findings", h2_style))
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(findings, key=lambda f: order.get(f.get("severity", "info"), 5))

    for i, finding in enumerate(sorted_findings, 1):
        sev = finding.get("severity", "info").lower()
        title = finding.get("title", "Untitled")
        sev_color = sev_colors.get(sev, HexColor("#58a6ff"))

        title_para = ParagraphStyle(f"Sev{i}", parent=h3_style, textColor=sev_color)
        story.append(Paragraph(f"{i}. [{sev.upper()}] {title}", title_para))
        if finding.get("description"):
            story.append(Paragraph(f"<b>Description:</b> {finding['description']}", body_style))
        if finding.get("remediation"):
            story.append(Paragraph(f"<b>Remediation:</b> {finding['remediation']}", body_style))
        story.append(HRFlowable(width="100%", color=HexColor("#30363d")))
        story.append(Spacer(1, 0.2*cm))

    doc.build(story)
