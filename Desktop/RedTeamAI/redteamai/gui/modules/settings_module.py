"""Settings module — AI backend config, tool paths, UI preferences."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTabWidget, QFormLayout, QGroupBox, QCheckBox, QComboBox, QSpinBox,
    QFrame, QScrollArea, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from redteamai.config.settings import AppSettings


class _SimpleDialog:
    """Placeholder to avoid import issues."""
    pass


class SettingsModule(QWidget):
    settings_changed = pyqtSignal(AppSettings)
    health_check_requested = pyqtSignal(str)

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self._settings = settings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background:#161b22; border-bottom:1px solid #30363d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 10, 16, 10)
        title = QLabel("Settings")
        title.setObjectName("heading")
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self._save_settings)
        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(save_btn)
        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_ai_tab(), "AI Backends")
        tabs.addTab(self._build_tools_tab(), "Tool Paths")
        tabs.addTab(self._build_ui_tab(), "UI / Behavior")
        tabs.addTab(self._build_about_tab(), "About")
        layout.addWidget(tabs)

    def _build_ai_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; }")

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Active backend
        backend_group = QGroupBox("Active AI Backend")
        backend_lay = QFormLayout(backend_group)
        self._backend_combo = QComboBox()
        self._backend_combo.addItems(["ollama", "groq", "anthropic", "openai_compat"])
        self._backend_combo.setCurrentText(self._settings.ai_backend)
        backend_lay.addRow("Backend:", self._backend_combo)
        layout.addWidget(backend_group)

        # Ollama
        ollama_group = QGroupBox("Ollama (Free Local — Recommended)")
        ollama_group.setStyleSheet("QGroupBox { border-top: 3px solid #3fb950; }")
        ollama_lay = QFormLayout(ollama_group)
        self._ollama_host = QLineEdit(self._settings.ollama.host)
        self._ollama_model = QLineEdit(self._settings.ollama.model)
        self._ollama_model.setPlaceholderText("e.g. llama3.1:8b, qwen2.5:7b, mistral:7b")
        ollama_check_btn = QPushButton("Health Check")
        ollama_check_btn.clicked.connect(lambda: self.health_check_requested.emit("ollama"))
        ollama_lay.addRow("Host:", self._ollama_host)
        ollama_lay.addRow("Model:", self._ollama_model)
        ollama_lay.addRow("", ollama_check_btn)
        ollama_note = QLabel("Free & private. Install: https://ollama.com  |  Pull model: ollama pull llama3.1")
        ollama_note.setObjectName("muted")
        ollama_note.setWordWrap(True)
        ollama_note.setStyleSheet("background:transparent;")
        ollama_lay.addRow(ollama_note)
        layout.addWidget(ollama_group)

        # Groq
        groq_group = QGroupBox("Groq (Free Tier — Fast)")
        groq_group.setStyleSheet("QGroupBox { border-top: 3px solid #58a6ff; }")
        groq_lay = QFormLayout(groq_group)
        self._groq_key = QLineEdit(self._settings.groq.api_key)
        self._groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._groq_key.setPlaceholderText("gsk_…")
        self._groq_model = QLineEdit(self._settings.groq.model)
        groq_check_btn = QPushButton("Health Check")
        groq_check_btn.clicked.connect(lambda: self.health_check_requested.emit("groq"))
        groq_lay.addRow("API Key:", self._groq_key)
        groq_lay.addRow("Model:", self._groq_model)
        groq_lay.addRow("", groq_check_btn)
        groq_note = QLabel("Free tier: https://console.groq.com — very fast inference")
        groq_note.setObjectName("muted")
        groq_note.setStyleSheet("background:transparent;")
        groq_lay.addRow(groq_note)
        layout.addWidget(groq_group)

        # Anthropic
        anthro_group = QGroupBox("Anthropic (Claude)")
        anthro_group.setStyleSheet("QGroupBox { border-top: 3px solid #bc8cff; }")
        anthro_lay = QFormLayout(anthro_group)
        self._anthropic_key = QLineEdit(self._settings.anthropic.api_key)
        self._anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._anthropic_key.setPlaceholderText("sk-ant-…")
        self._anthropic_model = QLineEdit(self._settings.anthropic.model)
        anthro_check_btn = QPushButton("Health Check")
        anthro_check_btn.clicked.connect(lambda: self.health_check_requested.emit("anthropic"))
        anthro_lay.addRow("API Key:", self._anthropic_key)
        anthro_lay.addRow("Model:", self._anthropic_model)
        anthro_lay.addRow("", anthro_check_btn)
        layout.addWidget(anthro_group)

        # OpenAI Compat
        openai_group = QGroupBox("OpenAI-Compatible (OpenAI, LM Studio, Together, etc.)")
        openai_lay = QFormLayout(openai_group)
        self._openai_key = QLineEdit(self._settings.openai_compat.api_key)
        self._openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._openai_base = QLineEdit(self._settings.openai_compat.base_url)
        self._openai_model = QLineEdit(self._settings.openai_compat.model)
        openai_lay.addRow("API Key:", self._openai_key)
        openai_lay.addRow("Base URL:", self._openai_base)
        openai_lay.addRow("Model:", self._openai_model)
        layout.addWidget(openai_group)

        # Agent settings
        agent_group = QGroupBox("Agent Behavior")
        agent_lay = QFormLayout(agent_group)
        self._max_iter = QSpinBox()
        self._max_iter.setRange(1, 20)
        self._max_iter.setValue(self._settings.max_agent_iterations)
        self._confirm_dangerous = QCheckBox("Require confirmation before dangerous tools")
        self._confirm_dangerous.setChecked(self._settings.require_confirm_dangerous)
        agent_lay.addRow("Max Iterations:", self._max_iter)
        agent_lay.addRow("", self._confirm_dangerous)
        layout.addWidget(agent_group)

        layout.addStretch()
        scroll.setWidget(w)
        return scroll

    def _build_tools_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; }")

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        tools_group = QGroupBox("Tool Binary Paths")
        tools_lay = QFormLayout(tools_group)
        tools = self._settings.tools

        self._tool_edits: dict[str, QLineEdit] = {}
        for field_name in ["nmap", "whois", "dig", "gobuster", "ffuf", "nikto",
                           "whatweb", "theharvester", "subfinder", "searchsploit"]:
            edit = QLineEdit(getattr(tools, field_name, ""))
            self._tool_edits[field_name] = edit
            tools_lay.addRow(f"{field_name}:", edit)

        layout.addWidget(tools_group)

        msf_group = QGroupBox("Metasploit RPC")
        msf_lay = QFormLayout(msf_group)
        self._msf_host = QLineEdit(tools.metasploit_rpc_host)
        self._msf_port = QSpinBox()
        self._msf_port.setRange(1, 65535)
        self._msf_port.setValue(tools.metasploit_rpc_port)
        self._msf_pass = QLineEdit(tools.metasploit_rpc_password)
        self._msf_pass.setEchoMode(QLineEdit.EchoMode.Password)
        msf_lay.addRow("RPC Host:", self._msf_host)
        msf_lay.addRow("RPC Port:", self._msf_port)
        msf_lay.addRow("Password:", self._msf_pass)
        layout.addWidget(msf_group)
        layout.addStretch()

        scroll.setWidget(w)
        return scroll

    def _build_ui_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        ui_group = QGroupBox("Interface")
        ui_lay = QFormLayout(ui_group)
        self._font_size = QSpinBox()
        self._font_size.setRange(9, 20)
        self._font_size.setValue(self._settings.font_size)
        self._auto_save = QCheckBox("Auto-save sessions")
        self._auto_save.setChecked(self._settings.auto_save_session)
        ui_lay.addRow("Font Size:", self._font_size)
        ui_lay.addRow("", self._auto_save)
        layout.addWidget(ui_group)
        layout.addStretch()
        return w

    def _build_about_tab(self) -> QWidget:
        from redteamai.constants import APP_VERSION, APP_NAME, APP_URL
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = QLabel("🔴 RedTeam AI")
        logo.setStyleSheet("font-size:24px; font-weight:bold; color:#f85149; background:transparent;")
        ver = QLabel(f"Version {APP_VERSION}")
        ver.setObjectName("subheading")
        desc = QLabel(
            "An open-source, AI-powered desktop application for authorized\n"
            "penetration testing, CTF competitions, and security research.\n\n"
            "Built with PyQt6, SQLAlchemy, and multiple AI backends."
        )
        desc.setObjectName("muted")
        desc.setWordWrap(True)
        desc.setStyleSheet("background:transparent;")
        url = QLabel(f'<a href="{APP_URL}" style="color:#58a6ff;">{APP_URL}</a>')
        url.setOpenExternalLinks(True)
        url.setStyleSheet("background:transparent;")

        license_lbl = QLabel("License: MIT — Free for authorized testing and research")
        license_lbl.setObjectName("muted")
        license_lbl.setStyleSheet("background:transparent;")

        layout.addWidget(logo)
        layout.addWidget(ver)
        layout.addWidget(desc)
        layout.addWidget(url)
        layout.addWidget(license_lbl)
        return w

    def _save_settings(self) -> None:
        from redteamai.config.settings import AppSettings, OllamaSettings, GroqSettings, AnthropicSettings, OpenAICompatSettings, ToolPaths

        s = self._settings
        s.ai_backend = self._backend_combo.currentText()
        s.ollama.host = self._ollama_host.text()
        s.ollama.model = self._ollama_model.text()
        s.groq.api_key = self._groq_key.text()
        s.groq.model = self._groq_model.text()
        s.anthropic.api_key = self._anthropic_key.text()
        s.anthropic.model = self._anthropic_model.text()
        s.openai_compat.api_key = self._openai_key.text()
        s.openai_compat.base_url = self._openai_base.text()
        s.openai_compat.model = self._openai_model.text()
        s.max_agent_iterations = self._max_iter.value()
        s.require_confirm_dangerous = self._confirm_dangerous.isChecked()
        s.font_size = self._font_size.value()
        s.auto_save_session = self._auto_save.isChecked()

        for field_name, edit in self._tool_edits.items():
            setattr(s.tools, field_name, edit.text())
        s.tools.metasploit_rpc_host = self._msf_host.text()
        s.tools.metasploit_rpc_port = self._msf_port.value()
        s.tools.metasploit_rpc_password = self._msf_pass.text()

        self.settings_changed.emit(s)
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

    def update_settings(self, settings: AppSettings) -> None:
        self._settings = settings
