"""Reporting module — generate and export findings reports."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLineEdit,
    QFileDialog, QSplitter, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from redteamai.gui.widgets.finding_badge import FindingBadge


class ReportingModule(QWidget):
    generate_report = pyqtSignal(str, str)  # (format, path)
    ask_ai = pyqtSignal(str)
    export_finding = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._findings: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background:#161b22; border-bottom:1px solid #30363d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Reporting")
        title.setObjectName("heading")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: findings list ───────────────────────────────────────────
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(8)

        left_header = QHBoxLayout()
        findings_label = QLabel("Findings")
        findings_label.setStyleSheet("font-weight:bold; color:#8b949e;")
        add_finding_btn = QPushButton("+ Add Finding")
        add_finding_btn.setObjectName("primary")
        add_finding_btn.setFixedHeight(32)
        add_finding_btn.clicked.connect(self._add_finding)
        left_header.addWidget(findings_label)
        left_header.addStretch()
        left_header.addWidget(add_finding_btn)
        left_layout.addLayout(left_header)

        self._findings_table = QTableWidget()
        self._findings_table.setColumnCount(3)
        self._findings_table.setHorizontalHeaderLabels(["Severity", "Title", "Status"])
        self._findings_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._findings_table.setAlternatingRowColors(True)
        self._findings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._findings_table.itemClicked.connect(self._on_finding_selected)
        left_layout.addWidget(self._findings_table)

        # ── Right: report generation ──────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)

        # Report config
        config_group = QGroupBox("Report Configuration")
        config_lay = QVBoxLayout(config_group)

        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Format:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["Markdown (.md)", "HTML (.html)", "PDF (.pdf)"])
        format_row.addWidget(self._format_combo)
        format_row.addStretch()
        config_lay.addLayout(format_row)

        gen_row = QHBoxLayout()
        gen_btn = QPushButton("📋 Generate Report")
        gen_btn.setObjectName("primary")
        gen_btn.setFixedHeight(38)
        gen_btn.clicked.connect(self._generate_report)
        ai_summary_btn = QPushButton("🤖 AI Executive Summary")
        ai_summary_btn.setFixedHeight(38)
        ai_summary_btn.clicked.connect(self._ai_summary)
        gen_row.addWidget(gen_btn)
        gen_row.addWidget(ai_summary_btn)
        config_lay.addLayout(gen_row)
        right_layout.addWidget(config_group)

        # Preview
        preview_label = QLabel("Report Preview")
        preview_label.setStyleSheet("font-weight:bold; color:#8b949e;")
        right_layout.addWidget(preview_label)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setStyleSheet("background:#0d1117; color:#c9d1d9; border:1px solid #30363d; border-radius:6px;")
        right_layout.addWidget(self._preview)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def load_findings(self, findings: list[dict]) -> None:
        self._findings = findings
        self._refresh_table()

    def add_finding_data(self, finding: dict) -> None:
        self._findings.append(finding)
        self._refresh_table()

    def set_preview(self, text: str) -> None:
        self._preview.setMarkdown(text)

    def _refresh_table(self) -> None:
        self._findings_table.setRowCount(len(self._findings))
        for row, f in enumerate(self._findings):
            sev_item = QTableWidgetItem(f.get("severity", "info").upper())
            color_map = {
                "critical": "#ff4444", "high": "#f85149",
                "medium": "#d29922", "low": "#3fb950", "info": "#58a6ff"
            }
            sev = f.get("severity", "info")
            from PyQt6.QtGui import QColor
            sev_item.setForeground(QColor(color_map.get(sev, "#58a6ff")))
            self._findings_table.setItem(row, 0, sev_item)
            self._findings_table.setItem(row, 1, QTableWidgetItem(f.get("title", "")))
            self._findings_table.setItem(row, 2, QTableWidgetItem(f.get("status", "open")))

    def _on_finding_selected(self, item) -> None:
        row = item.row()
        if row < len(self._findings):
            f = self._findings[row]
            text = f"# {f.get('title', '')}\n\n**Severity:** {f.get('severity', '').upper()}\n\n{f.get('description', '')}\n\n**Remediation:**\n{f.get('remediation', 'Not specified')}"
            self._preview.setMarkdown(text)

    def _add_finding(self) -> None:
        from redteamai.gui.modules.settings_module import _SimpleDialog
        from PyQt6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox, QComboBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Finding")
        dlg.setModal(True)
        dlg.setMinimumWidth(400)
        dlg.setStyleSheet("QDialog { background: #161b22; }")

        layout = QVBoxLayout(dlg)
        form = QFormLayout()
        title_edit = QLineEdit()
        severity_combo = QComboBox()
        severity_combo.addItems(["critical", "high", "medium", "low", "info"])
        severity_combo.setCurrentIndex(4)
        desc_edit = QTextEdit()
        desc_edit.setMaximumHeight(80)
        remed_edit = QTextEdit()
        remed_edit.setMaximumHeight(60)

        form.addRow("Title:", title_edit)
        form.addRow("Severity:", severity_combo)
        form.addRow("Description:", desc_edit)
        form.addRow("Remediation:", remed_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save Finding")
        save.setObjectName("primary")
        cancel.clicked.connect(dlg.reject)
        save.clicked.connect(dlg.accept)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted and title_edit.text().strip():
            self.add_finding_data({
                "title": title_edit.text().strip(),
                "severity": severity_combo.currentText(),
                "description": desc_edit.toPlainText(),
                "remediation": remed_edit.toPlainText(),
                "status": "open",
            })

    def _generate_report(self) -> None:
        fmt_map = {"Markdown (.md)": ("md", "Markdown Files (*.md)"),
                   "HTML (.html)": ("html", "HTML Files (*.html)"),
                   "PDF (.pdf)": ("pdf", "PDF Files (*.pdf)")}
        fmt_text = self._format_combo.currentText()
        ext, filter_str = fmt_map.get(fmt_text, ("md", "Markdown Files (*.md)"))

        path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"report.{ext}", filter_str)
        if path:
            self.generate_report.emit(ext, path)

    def _ai_summary(self) -> None:
        if self._findings:
            summary = "\n".join(f"- [{f.get('severity','info').upper()}] {f.get('title','')}" for f in self._findings)
            self.ask_ai.emit(f"Write a professional executive summary for these penetration testing findings:\n{summary}")
