"""ANSI-color-aware terminal output widget."""
from __future__ import annotations
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal
from redteamai.utils.ansi_parser import parse_ansi


class TerminalOutput(QPlainTextEdit):
    """Read-only terminal widget with ANSI color support."""

    copy_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("terminal")
        self.setReadOnly(True)
        self.setMaximumBlockCount(5000)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._default_fmt = QTextCharFormat()
        self._default_fmt.setForeground(QColor("#00ff41"))

    def append_ansi(self, text: str) -> None:
        """Append text with ANSI color codes rendered as Qt colors."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        spans = parse_ansi(text)
        for span in spans:
            if not span.text:
                continue
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(span.fg) if span.fg else QColor("#00ff41"))
            if span.bg:
                fmt.setBackground(QColor(span.bg))
            if span.bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            if span.italic:
                fmt.setFontItalic(True)
            cursor.insertText(span.text, fmt)

        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def append_line(self, text: str, color: str | None = None) -> None:
        """Append a plain line, optionally with a color."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color) if color else QColor("#00ff41"))
        cursor.insertText(text + "\n", fmt)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def clear_output(self) -> None:
        self.clear()

    def get_full_text(self) -> str:
        return self.toPlainText()

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy()
        super().keyPressEvent(event)


class TerminalWidget(QWidget):
    """Terminal output with toolbar (clear, copy)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setFixedWidth(60)
        self._copy_btn = QPushButton("Copy All")
        self._copy_btn.setFixedWidth(80)

        toolbar.addStretch()
        toolbar.addWidget(self._copy_btn)
        toolbar.addWidget(self._clear_btn)

        self.terminal = TerminalOutput()
        layout.addLayout(toolbar)
        layout.addWidget(self.terminal)

        self._clear_btn.clicked.connect(self.terminal.clear_output)
        self._copy_btn.clicked.connect(self._copy_all)

    def _copy_all(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.terminal.get_full_text())

    def append_ansi(self, text: str) -> None:
        self.terminal.append_ansi(text)

    def append_line(self, text: str, color: str | None = None) -> None:
        self.terminal.append_line(text, color)

    def clear_output(self) -> None:
        self.terminal.clear_output()
