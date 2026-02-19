"""Custom status bar with spinner and job status."""
from __future__ import annotations
from PyQt6.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from redteamai.gui.widgets.job_indicator import SpinnerWidget


class AppStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(False)

        # Left: status message
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("muted")
        self.addWidget(self._status_label, 1)

        # Right side container
        right = QWidget()
        rl = QHBoxLayout(right)
        rl.setContentsMargins(0, 0, 8, 0)
        rl.setSpacing(6)

        # AI spinner
        self._ai_spinner = SpinnerWidget(16, "#1f6feb")
        self._ai_label = QLabel("")
        self._ai_label.setObjectName("muted")
        self._ai_label.hide()

        # Tool spinner
        self._tool_spinner = SpinnerWidget(16, "#3fb950")
        self._tool_label = QLabel("")
        self._tool_label.setObjectName("muted")
        self._tool_label.hide()

        # Backend indicator
        self._backend_label = QLabel("● Ollama")
        self._backend_label.setObjectName("accent")

        rl.addWidget(self._ai_spinner)
        rl.addWidget(self._ai_label)
        rl.addWidget(self._tool_spinner)
        rl.addWidget(self._tool_label)
        rl.addWidget(self._backend_label)

        self.addPermanentWidget(right)

    def set_status(self, msg: str) -> None:
        self._status_label.setText(msg)

    def set_ai_busy(self, busy: bool, msg: str = "AI thinking…") -> None:
        if busy:
            self._ai_spinner.start()
            self._ai_label.setText(msg)
            self._ai_label.show()
        else:
            self._ai_spinner.stop()
            self._ai_label.hide()

    def set_tool_busy(self, busy: bool, msg: str = "Tool running…") -> None:
        if busy:
            self._tool_spinner.start()
            self._tool_label.setText(msg)
            self._tool_label.show()
        else:
            self._tool_spinner.stop()
            self._tool_label.hide()

    def set_backend(self, name: str, healthy: bool = True) -> None:
        color = "#3fb950" if healthy else "#f85149"
        self._backend_label.setText(f"● {name.title()}")
        self._backend_label.setStyleSheet(f"color: {color};")
