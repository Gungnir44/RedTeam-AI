"""Syntax-highlighted code block widget with one-click copy."""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from redteamai.gui.styles.syntax_highlight import CodeHighlighter


class CodeBlock(QWidget):
    """Syntax-highlighted, copyable code display widget."""

    def __init__(self, code: str = "", language: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setObjectName("card")
        header.setStyleSheet("background:#21262d; border-radius:6px 6px 0 0; border-bottom:1px solid #30363d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(8, 4, 8, 4)

        lang_label = QLabel(language or "output")
        lang_label.setObjectName("muted")
        lang_label.setStyleSheet("font-size:11px; background:transparent;")

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(50, 22)
        copy_btn.setStyleSheet("font-size:11px; padding:2px 6px;")
        copy_btn.clicked.connect(self._copy)

        hl.addWidget(lang_label)
        hl.addStretch()
        hl.addWidget(copy_btn)

        # Code area
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._editor.setStyleSheet(
            "background:#0d1117; border:1px solid #30363d; border-top:none; "
            "border-radius:0 0 6px 6px; padding:8px; color:#c9d1d9; font-size:12px;"
        )
        self._highlighter = CodeHighlighter(self._editor.document())

        if code:
            self._editor.setPlainText(code)

        layout.addWidget(header)
        layout.addWidget(self._editor)

    def set_code(self, code: str) -> None:
        self._editor.setPlainText(code)

    def _copy(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._editor.toPlainText())


class InlineCode(QLabel):
    """Inline code span (monospace, slightly highlighted)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            "background:#21262d; color:#c9d1d9; border:1px solid #30363d; "
            "border-radius:3px; padding:1px 4px; font-family:monospace; font-size:12px;"
        )
