"""Dashboard module — project overview and quick actions."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class StatCard(QFrame):
    def __init__(self, title: str, value: str, color: str = "#58a6ff", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(f"background:#161b22; border:1px solid #30363d; border-radius:8px; border-top: 3px solid {color};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size:28px; font-weight:bold; color:{color}; background:transparent;")

        title_lbl = QLabel(title)
        title_lbl.setObjectName("muted")
        title_lbl.setStyleSheet("background:transparent;")

        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)

    def set_value(self, value: str) -> None:
        self.layout().itemAt(0).widget().setText(value)


class DashboardModule(QWidget):
    new_project_requested = pyqtSignal()
    open_project_requested = pyqtSignal(int)
    module_navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Header
        title = QLabel("Dashboard")
        title.setObjectName("heading")
        subtitle = QLabel("Welcome to RedTeam AI — your authorized penetration testing assistant")
        subtitle.setObjectName("subheading")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Stats row
        stats_layout = QHBoxLayout()
        self._hosts_card    = StatCard("Hosts Discovered", "0", "#58a6ff")
        self._findings_card = StatCard("Findings",         "0", "#f85149")
        self._tools_card    = StatCard("Tools Available",  "0", "#3fb950")
        self._sessions_card = StatCard("Sessions",         "0", "#d29922")

        for card in [self._hosts_card, self._findings_card, self._tools_card, self._sessions_card]:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        # Quick actions
        qa_label = QLabel("Quick Actions")
        qa_label.setStyleSheet("font-size:14px; font-weight:bold; color:#8b949e;")
        layout.addWidget(qa_label)

        actions = QHBoxLayout()
        quick_actions = [
            ("🎯  New Target", "targets", "#1f6feb"),
            ("🔍  Run Recon",  "recon",   "#3fb950"),
            ("🌐  Web Scan",   "web_scan","#d29922"),
            ("🚩  CTF Solver", "ctf",     "#bc8cff"),
        ]
        for label, module, color in quick_actions:
            btn = QPushButton(label)
            btn.setFixedHeight(44)
            btn.setStyleSheet(f"background:{color}22; border:1px solid {color}; border-radius:8px; color:{color}; font-weight:bold; font-size:13px;")
            btn.clicked.connect(lambda _, m=module: self.module_navigate.emit(m))
            actions.addWidget(btn)
        layout.addLayout(actions)

        # Recent activity
        recent_label = QLabel("Getting Started")
        recent_label.setStyleSheet("font-size:14px; font-weight:bold; color:#8b949e;")
        layout.addWidget(recent_label)

        tips = QFrame()
        tips.setObjectName("card")
        tips.setStyleSheet("background:#161b22; border:1px solid #30363d; border-radius:8px; padding:4px;")
        tips_layout = QVBoxLayout(tips)
        tips_layout.setContentsMargins(16, 12, 16, 12)
        tips_layout.setSpacing(8)

        tip_items = [
            "1. Go to Settings → configure your AI backend (Ollama recommended for free local AI)",
            "2. Add a target in the Targets module",
            "3. Use Recon module to scan with Nmap, Whois, Dig",
            "4. Ask the AI assistant for analysis and next steps",
            "5. Document findings and generate a professional report",
        ]
        for tip in tip_items:
            lbl = QLabel(tip)
            lbl.setObjectName("muted")
            lbl.setStyleSheet("background:transparent;")
            lbl.setWordWrap(True)
            tips_layout.addWidget(lbl)

        layout.addWidget(tips)
        layout.addStretch()

    def update_stats(self, hosts: int = 0, findings: int = 0, tools: int = 0, sessions: int = 0) -> None:
        self._hosts_card.set_value(str(hosts))
        self._findings_card.set_value(str(findings))
        self._tools_card.set_value(str(tools))
        self._sessions_card.set_value(str(sessions))
