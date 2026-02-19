"""Web Scanning module — Gobuster, ffuf, Nikto, WhatWeb."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTabWidget, QComboBox, QFormLayout, QGroupBox, QSpinBox, QSplitter,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from redteamai.gui.widgets.terminal_output import TerminalWidget
from redteamai.gui.widgets.collapsible_section import CollapsibleSection


class WebScanModule(QWidget):
    run_tool = pyqtSignal(str, dict)
    ask_ai = pyqtSignal(str)
    save_to_project = pyqtSignal(str, str)

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
        title = QLabel("Web Scanning")
        title.setObjectName("heading")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left ──────────────────────────────────────────────────────────
        left = QWidget()
        left.setMinimumWidth(300)
        left.setMaximumWidth(400)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        # URL input
        url_group = QGroupBox("Target URL")
        url_lay = QVBoxLayout(url_group)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("http://target.com")
        url_lay.addWidget(self._url_input)
        left_layout.addWidget(url_group)

        # WhatWeb
        whatweb_section = CollapsibleSection("WhatWeb Fingerprinting", expanded=True)
        whatweb_inner = QWidget()
        whatweb_lay = QFormLayout(whatweb_inner)
        self._whatweb_aggression = QComboBox()
        self._whatweb_aggression.addItems(["1 (Passive)", "3 (Aggressive)", "4 (Heavy)"])
        whatweb_lay.addRow("Aggression:", self._whatweb_aggression)
        whatweb_btn = QPushButton("Run WhatWeb")
        whatweb_btn.clicked.connect(self._run_whatweb)
        ww_container_lay = QVBoxLayout()
        ww_container_lay.addWidget(whatweb_inner)
        ww_container_lay.addWidget(whatweb_btn)
        ww_container = QWidget()
        ww_container.setLayout(ww_container_lay)
        whatweb_section.add_widget(ww_container)
        left_layout.addWidget(whatweb_section)

        # Nikto
        nikto_section = CollapsibleSection("Nikto Vuln Scanner", expanded=False)
        nikto_btn = QPushButton("Run Nikto")
        nikto_btn.clicked.connect(self._run_nikto)
        nikto_section.add_widget(nikto_btn)
        left_layout.addWidget(nikto_section)

        # Gobuster
        gobuster_section = CollapsibleSection("Gobuster Dir Brute", expanded=False)
        gobuster_inner = QWidget()
        gobuster_lay = QFormLayout(gobuster_inner)
        self._gobuster_wordlist = QLineEdit()
        self._gobuster_wordlist.setPlaceholderText("/usr/share/wordlists/dirb/common.txt")
        self._gobuster_ext = QLineEdit()
        self._gobuster_ext.setPlaceholderText("php,html,txt")
        self._gobuster_threads = QSpinBox()
        self._gobuster_threads.setRange(1, 50)
        self._gobuster_threads.setValue(10)
        gobuster_lay.addRow("Wordlist:", self._gobuster_wordlist)
        gobuster_lay.addRow("Extensions:", self._gobuster_ext)
        gobuster_lay.addRow("Threads:", self._gobuster_threads)
        gobuster_btn = QPushButton("Run Gobuster")
        gobuster_btn.setObjectName("danger")
        gobuster_btn.clicked.connect(self._run_gobuster)
        gb_container_lay = QVBoxLayout()
        gb_container_lay.addWidget(gobuster_inner)
        gb_container_lay.addWidget(gobuster_btn)
        gb_container = QWidget()
        gb_container.setLayout(gb_container_lay)
        gobuster_section.add_widget(gb_container)
        left_layout.addWidget(gobuster_section)

        # ffuf
        ffuf_section = CollapsibleSection("ffuf Fuzzer", expanded=False)
        ffuf_inner = QWidget()
        ffuf_lay = QFormLayout(ffuf_inner)
        self._ffuf_wordlist = QLineEdit()
        self._ffuf_wordlist.setPlaceholderText("/usr/share/wordlists/dirb/common.txt")
        ffuf_lay.addRow("Wordlist:", self._ffuf_wordlist)
        ffuf_note = QLabel("Add FUZZ placeholder to URL")
        ffuf_note.setObjectName("muted")
        ffuf_note.setStyleSheet("background:transparent;")
        ffuf_btn = QPushButton("Run ffuf")
        ffuf_btn.setObjectName("danger")
        ffuf_btn.clicked.connect(self._run_ffuf)
        ffuf_container_lay = QVBoxLayout()
        ffuf_container_lay.addWidget(ffuf_inner)
        ffuf_container_lay.addWidget(ffuf_note)
        ffuf_container_lay.addWidget(ffuf_btn)
        ffuf_container = QWidget()
        ffuf_container.setLayout(ffuf_container_lay)
        ffuf_section.add_widget(ffuf_container)
        left_layout.addWidget(ffuf_section)

        left_layout.addStretch()

        # ── Right ─────────────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(6)

        output_header = QHBoxLayout()
        self._tool_label = QLabel("Output")
        self._tool_label.setObjectName("subheading")
        ai_btn = QPushButton("🤖 Analyze with AI")
        ai_btn.setObjectName("primary")
        ai_btn.clicked.connect(self._analyze_with_ai)
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self._save)
        output_header.addWidget(self._tool_label)
        output_header.addStretch()
        output_header.addWidget(ai_btn)
        output_header.addWidget(save_btn)

        self._terminal = TerminalWidget()
        right_layout.addLayout(output_header)
        right_layout.addWidget(self._terminal)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def set_url(self, url: str) -> None:
        self._url_input.setText(url)

    def append_output(self, text: str) -> None:
        self._terminal.append_ansi(text)

    def set_tool_busy(self, busy: bool, tool: str = "") -> None:
        if busy:
            self._tool_label.setText(f"Running: {tool}…")
        else:
            self._tool_label.setText("Output")

    def _get_url(self) -> str:
        return self._url_input.text().strip()

    def _run_whatweb(self) -> None:
        url = self._get_url()
        if url:
            agg = self._whatweb_aggression.currentText()[0]
            self.run_tool.emit("whatweb", {"target": url, "aggression": agg})

    def _run_nikto(self) -> None:
        url = self._get_url()
        if url:
            self.run_tool.emit("nikto", {"target": url})

    def _run_gobuster(self) -> None:
        url = self._get_url()
        wl = self._gobuster_wordlist.text().strip()
        if url and wl:
            self.run_tool.emit("gobuster", {
                "url": url,
                "wordlist": wl,
                "extensions": self._gobuster_ext.text().strip(),
                "threads": self._gobuster_threads.value(),
            })

    def _run_ffuf(self) -> None:
        url = self._get_url()
        wl = self._ffuf_wordlist.text().strip()
        if url and wl:
            target = url if "FUZZ" in url else url.rstrip("/") + "/FUZZ"
            self.run_tool.emit("ffuf", {"url": target, "wordlist": wl})

    def _analyze_with_ai(self) -> None:
        output = self._terminal.terminal.get_full_text()
        if output.strip():
            self.ask_ai.emit(f"Analyze this web scan output and identify vulnerabilities:\n\n```\n{output[:3000]}\n```")

    def _save(self) -> None:
        output = self._terminal.terminal.get_full_text()
        if output.strip():
            self.save_to_project.emit("Web Scan Output", output)
