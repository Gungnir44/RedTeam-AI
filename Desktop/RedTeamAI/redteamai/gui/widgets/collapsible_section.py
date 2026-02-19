"""Collapsible section widget (accordion-style)."""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QIcon


class CollapsibleSection(QWidget):
    """A widget that can be expanded/collapsed by clicking its header."""

    def __init__(self, title: str, parent=None, expanded: bool = True):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header button
        self._toggle = QPushButton(f"▼  {title}" if expanded else f"▶  {title}")
        self._toggle.setCheckable(True)
        self._toggle.setChecked(expanded)
        self._toggle.setStyleSheet("""
            QPushButton {
                background: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-weight: bold;
                color: #c9d1d9;
            }
            QPushButton:hover { background: #30363d; }
        """)
        self._toggle.clicked.connect(self._on_toggle)

        # Content container
        self._content = QWidget()
        self._content.setVisible(expanded)

        layout.addWidget(self._toggle)
        layout.addWidget(self._content)

        self._title = title

    def set_content_layout(self, content_layout) -> None:
        self._content.setLayout(content_layout)

    def _on_toggle(self) -> None:
        expanded = self._toggle.isChecked()
        self._toggle.setText(f"▼  {self._title}" if expanded else f"▶  {self._title}")
        self._content.setVisible(expanded)

    def add_widget(self, widget: QWidget) -> None:
        if self._content.layout() is None:
            from PyQt6.QtWidgets import QVBoxLayout as VL
            self._content.setLayout(VL())
        self._content.layout().addWidget(widget)
