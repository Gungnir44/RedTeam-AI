"""Target Manager module — add, view, edit hosts."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
    QTextEdit, QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut


class AddTargetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Target")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet("QDialog { background: #161b22; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)

        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("e.g. 192.168.1.1")
        self.hostname_edit = QLineEdit()
        self.hostname_edit.setPlaceholderText("e.g. target.local")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["unknown", "up", "down"])
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Scope notes, authorization details…")

        form.addRow("IP Address:", self.ip_edit)
        form.addRow("Hostname:", self.hostname_edit)
        form.addRow("Status:", self.status_combo)
        form.addRow("Notes:", self.notes_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel")
        save   = QPushButton("Add Target")
        save.setObjectName("primary")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

    def get_data(self) -> dict:
        return {
            "ip_address": self.ip_edit.text().strip(),
            "hostname":   self.hostname_edit.text().strip(),
            "status":     self.status_combo.currentText(),
            "notes":      self.notes_edit.toPlainText().strip(),
        }


class TargetManagerModule(QWidget):
    target_selected = pyqtSignal(dict)
    scan_requested  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hosts: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("Target Manager")
        title.setObjectName("heading")
        add_btn = QPushButton("+ Add Target")
        add_btn.setObjectName("primary")
        add_btn.setFixedHeight(36)
        add_btn.setShortcut(QKeySequence("Ctrl+T"))
        add_btn.clicked.connect(self._add_target)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter targets…")
        self._search.textChanged.connect(self._filter_table)
        layout.addWidget(self._search)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Status", "Open Ports", "Notes"])
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

        # Action bar
        action_row = QHBoxLayout()
        scan_btn   = QPushButton("🔍 Quick Scan Selected")
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        scan_btn.clicked.connect(self._scan_selected)
        delete_btn.clicked.connect(self._delete_selected)
        action_row.addWidget(scan_btn)
        action_row.addStretch()
        action_row.addWidget(delete_btn)
        layout.addLayout(action_row)

    def load_hosts(self, hosts: list[dict]) -> None:
        self._hosts = hosts
        self._refresh_table(hosts)

    def add_host(self, host: dict) -> None:
        self._hosts.append(host)
        self._refresh_table(self._hosts)

    def _refresh_table(self, hosts: list[dict]) -> None:
        self._table.setRowCount(len(hosts))
        for row, h in enumerate(hosts):
            self._table.setItem(row, 0, QTableWidgetItem(h.get("ip_address", "")))
            self._table.setItem(row, 1, QTableWidgetItem(h.get("hostname", "")))
            status = h.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            color_map = {"up": "#3fb950", "down": "#f85149", "unknown": "#8b949e"}
            status_item.setForeground(__import__('PyQt6.QtGui', fromlist=['QColor']).QColor(color_map.get(status, "#8b949e")))
            self._table.setItem(row, 2, status_item)
            ports = h.get("open_ports", {})
            ports_str = ", ".join(str(p) for p in ports.keys()) if isinstance(ports, dict) else str(ports)
            self._table.setItem(row, 3, QTableWidgetItem(ports_str))
            self._table.setItem(row, 4, QTableWidgetItem(h.get("notes", "")))

    def _filter_table(self, text: str) -> None:
        text = text.lower()
        filtered = [h for h in self._hosts if
                    text in h.get("ip_address", "").lower() or
                    text in h.get("hostname", "").lower()]
        self._refresh_table(filtered)

    def _add_target(self) -> None:
        dlg = AddTargetDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if data["ip_address"] or data["hostname"]:
                self.add_host(data)

    def _on_double_click(self, item) -> None:
        row = item.row()
        if row < len(self._hosts):
            self.target_selected.emit(self._hosts[row])

    def _scan_selected(self) -> None:
        row = self._table.currentRow()
        if row >= 0 and row < len(self._hosts):
            target = self._hosts[row].get("ip_address") or self._hosts[row].get("hostname")
            if target:
                self.scan_requested.emit(target)

    def _delete_selected(self) -> None:
        row = self._table.currentRow()
        if row >= 0 and row < len(self._hosts):
            target = self._hosts[row]
            reply = QMessageBox.question(
                self, "Delete Target",
                f"Remove {target.get('ip_address') or target.get('hostname')}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._hosts.pop(row)
                self._refresh_table(self._hosts)
