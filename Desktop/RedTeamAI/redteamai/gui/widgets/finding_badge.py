"""Severity badge widget."""
from __future__ import annotations
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class FindingBadge(QLabel):
    """Colored severity badge: Critical/High/Medium/Low/Info."""

    SEVERITY_LABELS = {
        "critical": "CRITICAL",
        "high":     "HIGH",
        "medium":   "MEDIUM",
        "low":      "LOW",
        "info":     "INFO",
    }

    def __init__(self, severity: str = "info", parent=None):
        super().__init__(parent)
        self.set_severity(severity)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_severity(self, severity: str) -> None:
        sev = severity.lower()
        label = self.SEVERITY_LABELS.get(sev, sev.upper())
        self.setText(label)
        self.setObjectName(f"badge_{sev}")
        # Re-apply style (object name change requires polish)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setToolTip(f"Severity: {label}")
