"""Pygments-based syntax highlighter for QSyntaxHighlighter."""
from __future__ import annotations
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class CodeHighlighter(QSyntaxHighlighter):
    """Simple syntax highlighter for common security tool output patterns."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._build_rules()

    def _fmt(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.Bold)
        if italic:
            f.setFontItalic(True)
        return f

    def _build_rules(self):
        rules = [
            # IP addresses
            (r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b', "#58a6ff", False),
            # Ports
            (r'\b(?:PORT|port)\s+\d+/\w+', "#d29922", True),
            # Open/closed/filtered
            (r'\bopen\b', "#3fb950", True),
            (r'\bclosed\b', "#f85149", False),
            (r'\bfiltered\b', "#d29922", False),
            # HTTP status codes
            (r'\b[25]\d{2}\b', "#3fb950", False),
            (r'\b[34]\d{2}\b', "#d29922", False),
            (r'\b[5]\d{2}\b', "#f85149", False),
            # CVE IDs
            (r'\bCVE-\d{4}-\d+\b', "#bc8cff", True),
            # URLs
            (r'https?://\S+', "#58a6ff", False),
            # Hex values
            (r'\b0x[0-9a-fA-F]+\b', "#e3b341", False),
            # Error/warning keywords
            (r'\b(?:ERROR|FAILED|CRITICAL|FATAL)\b', "#f85149", True),
            (r'\b(?:WARNING|WARN)\b', "#d29922", True),
            (r'\b(?:SUCCESS|OK|DONE)\b', "#3fb950", True),
            # Comments
            (r'#[^\n]*', "#6e7681", True),
            # Strings
            (r'"[^"]*"', "#a5d6ff", False),
            (r"'[^']*'", "#a5d6ff", False),
        ]

        for pattern, color, bold in rules:
            fmt = self._fmt(color, bold=bold)
            self._rules.append((QRegularExpression(pattern), fmt))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
