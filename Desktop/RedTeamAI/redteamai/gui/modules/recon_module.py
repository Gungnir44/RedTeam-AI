"""Reconnaissance module — Nmap, Whois, Dig, theHarvester, Subfinder."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTabWidget, QComboBox, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from redteamai.gui.widgets.terminal_output import TerminalWidget
from redteamai.gui.widgets.collapsible_section import CollapsibleSection


class ReconModule(QWidget):
    """Recon module: network scanning and OSINT."""

    run_tool = pyqtSignal(str, dict)  # (tool_name, kwargs)
    save_to_project = pyqtSignal(str, str)  # (label, content)
    ask_ai = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background:#161b22; border-bottom:1px solid #30363d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Reconnaissance")
        title.setObjectName("heading")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: tool forms ──────────────────────────────────────────────
        left = QWidget()
        left.setMinimumWidth(280)
        left.setMaximumWidth(380)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        # Target
        tgt_group = QGroupBox("Target")
        tgt_lay = QVBoxLayout(tgt_group)
        self._target_input = QLineEdit()
        self._target_input.setPlaceholderText("IP, hostname, or CIDR (e.g. 192.168.1.0/24)")
        tgt_lay.addWidget(self._target_input)
        left_layout.addWidget(tgt_group)

        # Nmap
        nmap_section = CollapsibleSection("Nmap Scanner", expanded=True)
        nmap_inner = QWidget()
        nmap_lay = QFormLayout(nmap_inner)
        nmap_lay.setSpacing(6)
        self._nmap_scan_type = QComboBox()
        self._nmap_scan_type.addItems(["sV (Version)", "sS (SYN)", "sT (TCP)", "sA (ACK)", "sn (Ping)", "A (Aggressive)", "O (OS)"])
        self._nmap_timing = QComboBox()
        self._nmap_timing.addItems(["T3 (Normal)", "T4 (Aggressive)", "T5 (Insane)", "T1 (Sneaky)", "T2 (Polite)"])
        self._nmap_timing.setCurrentIndex(1)
        self._nmap_ports = QLineEdit()
        self._nmap_ports.setPlaceholderText("e.g. 80,443,1-1024 (blank=top 1000)")
        self._nmap_extra = QLineEdit()
        self._nmap_extra.setPlaceholderText("e.g. --script vuln")

        nmap_lay.addRow("Scan Type:", self._nmap_scan_type)
        nmap_lay.addRow("Timing:", self._nmap_timing)
        nmap_lay.addRow("Ports:", self._nmap_ports)
        nmap_lay.addRow("Extra:", self._nmap_extra)

        nmap_btn = QPushButton("Run Nmap")
        nmap_btn.setObjectName("primary")
        nmap_btn.clicked.connect(self._run_nmap)
        nmap_inner_lay = QVBoxLayout()
        nmap_inner_lay.addWidget(nmap_inner)
        nmap_inner_lay.addWidget(nmap_btn)

        nmap_container = QWidget()
        nmap_container.setLayout(nmap_inner_lay)
        nmap_section.add_widget(nmap_container)
        left_layout.addWidget(nmap_section)

        # Whois
        whois_section = CollapsibleSection("Whois Lookup", expanded=False)
        whois_btn = QPushButton("Run Whois")
        whois_btn.clicked.connect(self._run_whois)
        whois_section.add_widget(whois_btn)
        left_layout.addWidget(whois_section)

        # Dig
        dig_section = CollapsibleSection("DNS Lookup (Dig)", expanded=False)
        dig_inner = QWidget()
        dig_lay = QFormLayout(dig_inner)
        self._dig_type = QComboBox()
        self._dig_type.addItems(["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "ANY"])
        self._dig_ns = QLineEdit()
        self._dig_ns.setPlaceholderText("Optional nameserver (e.g. 8.8.8.8)")
        dig_lay.addRow("Record Type:", self._dig_type)
        dig_lay.addRow("Nameserver:", self._dig_ns)
        dig_btn = QPushButton("Run Dig")
        dig_btn.clicked.connect(self._run_dig)
        dig_container_lay = QVBoxLayout()
        dig_container_lay.addWidget(dig_inner)
        dig_container_lay.addWidget(dig_btn)
        dig_container = QWidget()
        dig_container.setLayout(dig_container_lay)
        dig_section.add_widget(dig_container)
        left_layout.addWidget(dig_section)

        # theHarvester
        harv_section = CollapsibleSection("theHarvester", expanded=False)
        harv_btn = QPushButton("Run theHarvester")
        harv_btn.clicked.connect(self._run_harvester)
        harv_section.add_widget(harv_btn)
        left_layout.addWidget(harv_section)

        # Subfinder
        sub_section = CollapsibleSection("Subfinder", expanded=False)
        sub_btn = QPushButton("Run Subfinder")
        sub_btn.clicked.connect(self._run_subfinder)
        sub_section.add_widget(sub_btn)
        left_layout.addWidget(sub_section)

        left_layout.addStretch()

        # ── Right: output ─────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(6)

        output_header = QHBoxLayout()
        self._tool_label = QLabel("Output")
        self._tool_label.setObjectName("subheading")
        self._ai_btn = QPushButton("🤖 Analyze with AI")
        self._ai_btn.setObjectName("primary")
        self._ai_btn.clicked.connect(self._analyze_with_ai)
        self._save_btn = QPushButton("💾 Save to Project")
        self._save_btn.clicked.connect(self._save_to_project)

        output_header.addWidget(self._tool_label)
        output_header.addStretch()
        output_header.addWidget(self._ai_btn)
        output_header.addWidget(self._save_btn)

        self._terminal = TerminalWidget()
        right_layout.addLayout(output_header)
        right_layout.addWidget(self._terminal)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def set_target(self, target: str) -> None:
        self._target_input.setText(target)

    def append_output(self, text: str) -> None:
        self._terminal.append_ansi(text)

    def set_tool_busy(self, busy: bool, tool: str = "") -> None:
        if busy:
            self._tool_label.setText(f"Running: {tool}…")
        else:
            self._tool_label.setText("Output")

    def _get_target(self) -> str:
        return self._target_input.text().strip()

    def _run_nmap(self) -> None:
        target = self._get_target()
        if not target:
            return
        scan_map = {"sV (Version)": "sV", "sS (SYN)": "sS", "sT (TCP)": "sT",
                    "sA (ACK)": "sA", "sn (Ping)": "sn", "A (Aggressive)": "A", "O (OS)": "O"}
        timing_map = {"T3 (Normal)": "T3", "T4 (Aggressive)": "T4", "T5 (Insane)": "T5",
                      "T1 (Sneaky)": "T1", "T2 (Polite)": "T2"}
        self.run_tool.emit("nmap", {
            "target": target,
            "scan_type": scan_map.get(self._nmap_scan_type.currentText(), "sV"),
            "timing": timing_map.get(self._nmap_timing.currentText(), "T4"),
            "ports": self._nmap_ports.text().strip(),
            "extra_args": self._nmap_extra.text().strip(),
        })

    def _run_whois(self) -> None:
        target = self._get_target()
        if target:
            self.run_tool.emit("whois", {"target": target})

    def _run_dig(self) -> None:
        target = self._get_target()
        if target:
            self.run_tool.emit("dig", {
                "target": target,
                "record_type": self._dig_type.currentText(),
                "nameserver": self._dig_ns.text().strip(),
            })

    def _run_harvester(self) -> None:
        target = self._get_target()
        if target:
            self.run_tool.emit("theharvester", {"domain": target})

    def _run_subfinder(self) -> None:
        target = self._get_target()
        if target:
            self.run_tool.emit("subfinder", {"domain": target})

    def _analyze_with_ai(self) -> None:
        output = self._terminal.terminal.get_full_text()
        if output.strip():
            self.ask_ai.emit(f"Analyze this recon output and identify key findings:\n\n```\n{output[:3000]}\n```")

    def _save_to_project(self) -> None:
        output = self._terminal.terminal.get_full_text()
        if output.strip():
            self.save_to_project.emit("Recon Output", output)
