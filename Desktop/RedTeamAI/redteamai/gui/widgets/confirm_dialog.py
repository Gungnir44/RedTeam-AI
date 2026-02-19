"""Confirmation dialog for dangerous tool execution."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ConfirmDialog(QDialog):
    """
    Shows: "This will run: <command>. Proceed?"
    Returns True if user confirms, False if cancelled.
    """

    def __init__(self, tool_name: str, command: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Execution")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("QDialog { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Warning icon + title
        title_lbl = QLabel(f"⚠️  Execute: {tool_name}")
        title_lbl.setStyleSheet("font-size:15px; font-weight:bold; color:#d29922;")

        desc_lbl = QLabel("The AI agent wants to run the following command:")
        desc_lbl.setObjectName("muted")

        # Command preview
        cmd_view = QPlainTextEdit(command)
        cmd_view.setReadOnly(True)
        cmd_view.setMaximumHeight(80)
        cmd_view.setStyleSheet(
            "background:#0d1117; color:#00ff41; border:1px solid #30363d; "
            "border-radius:4px; padding:6px; font-family:monospace; font-size:12px;"
        )

        warn_lbl = QLabel("Only proceed if you have explicit authorization to test this target.")
        warn_lbl.setObjectName("danger")
        warn_lbl.setWordWrap(True)

        # Buttons
        btn_layout = QHBoxLayout()
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("danger")
        self._confirm_btn = QPushButton("Proceed")
        self._confirm_btn.setObjectName("success")

        btn_layout.addStretch()
        btn_layout.addWidget(self._cancel_btn)
        btn_layout.addWidget(self._confirm_btn)

        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addWidget(cmd_view)
        layout.addWidget(warn_lbl)
        layout.addLayout(btn_layout)

        self._cancel_btn.clicked.connect(self.reject)
        self._confirm_btn.clicked.connect(self.accept)

    @staticmethod
    def ask(tool_name: str, command: str, parent=None) -> bool:
        dlg = ConfirmDialog(tool_name, command, parent)
        return dlg.exec() == QDialog.DialogCode.Accepted
