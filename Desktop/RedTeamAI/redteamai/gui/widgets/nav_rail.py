"""Navigation rail widget — collapsible icon + label sidebar."""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont


NAV_ITEMS = [
    ("dashboard",     "⬛", "Dashboard"),
    ("targets",       "🎯", "Targets"),
    ("recon",         "🔍", "Recon"),
    ("web_scan",      "🌐", "Web Scan"),
    ("exploitation",  "💥", "Exploit"),
    ("ctf",           "🚩", "CTF"),
    ("reporting",     "📋", "Reports"),
    ("settings",      "⚙️", "Settings"),
]


class NavRail(QWidget):
    """Left navigation rail with collapsible labels."""

    module_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navRail")
        self._expanded = True
        self._buttons: dict[str, QPushButton] = {}
        self._active = "dashboard"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(2)

        # Toggle button
        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setObjectName("navBtn")
        self._toggle_btn.setFixedHeight(36)
        self._toggle_btn.setToolTip("Collapse sidebar")
        self._toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self._toggle_btn)

        # App title (visible when expanded)
        self._title = QLabel("RedTeam AI")
        self._title.setStyleSheet("color:#58a6ff; font-weight:bold; font-size:13px; padding:4px 8px; background:transparent;")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)

        layout.addSpacing(8)

        # Nav items
        for module_id, icon, label in NAV_ITEMS:
            btn = QPushButton(f"{icon}  {label}")
            btn.setObjectName("navBtn")
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setToolTip(label)
            btn.clicked.connect(lambda checked, mid=module_id: self._on_module_clicked(mid))
            layout.addWidget(btn)
            self._buttons[module_id] = btn

        layout.addStretch()

        # Version
        self._version_label = QLabel("v0.1.0")
        self._version_label.setObjectName("muted")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._version_label)

        self.setFixedWidth(200)
        self._activate("dashboard")

    def _on_module_clicked(self, module_id: str) -> None:
        self._activate(module_id)
        self.module_changed.emit(module_id)

    def _activate(self, module_id: str) -> None:
        for mid, btn in self._buttons.items():
            btn.setChecked(mid == module_id)
        self._active = module_id

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        if self._expanded:
            self.setFixedWidth(200)
            self._toggle_btn.setText("◀")
            self._title.show()
            self._version_label.show()
            for btn in self._buttons.values():
                icon, label = [(i, l) for m, i, l in NAV_ITEMS if m == list(self._buttons.keys())[list(self._buttons.values()).index(btn)]][0]
                btn.setText(f"{icon}  {label}")
        else:
            self.setFixedWidth(52)
            self._toggle_btn.setText("▶")
            self._title.hide()
            self._version_label.hide()
            for module_id, icon, label in NAV_ITEMS:
                if module_id in self._buttons:
                    self._buttons[module_id].setText(icon)

    def set_active(self, module_id: str) -> None:
        self._activate(module_id)
