"""Main application window: nav rail + module stack + AI chat panel."""
from __future__ import annotations
import asyncio
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QStackedWidget, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QKeySequence, QShortcut

from redteamai.app import AppState
from redteamai.gui.widgets.nav_rail import NavRail
from redteamai.gui.widgets.status_bar import AppStatusBar
from redteamai.gui.panels.ai_chat_panel import AIChatPanel
from redteamai.gui.widgets.confirm_dialog import ConfirmDialog
from redteamai.gui.modules.dashboard import DashboardModule
from redteamai.gui.modules.target_manager import TargetManagerModule
from redteamai.gui.modules.recon_module import ReconModule
from redteamai.gui.modules.web_scan_module import WebScanModule
from redteamai.gui.modules.exploitation_module import ExploitationModule
from redteamai.gui.modules.ctf_module import CTFModule
from redteamai.gui.modules.reporting_module import ReportingModule
from redteamai.gui.modules.settings_module import SettingsModule
from redteamai.tools.registry import build_default_registry, ToolRegistry
from redteamai.workers.tool_worker import ToolWorker
from redteamai.workers.ai_worker import AIWorker
from redteamai.ai.backend_factory import create_backend
from redteamai.ai.agent import RedTeamAgent
from redteamai.ai.message_history import MessageHistory
from redteamai.ai.prompt_templates import get_prompt
from redteamai.utils.logger import get_logger

log = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, app_state: AppState):
        super().__init__()
        self.app_state = app_state
        self._tool_worker: Optional[ToolWorker] = None
        self._ai_worker: Optional[AIWorker] = None
        self._current_tool_bubble = None
        self._tool_output_buffer = ""

        self._setup_registry()
        self._setup_ui()
        self._setup_shortcuts()
        self._setup_connections()
        self._update_status_bar_backend()

    def _setup_registry(self) -> None:
        self._registry = build_default_registry(self.app_state.settings)
        log.info(f"Tool registry loaded: {len(self._registry.list_tools())} tools")

    def _setup_ui(self) -> None:
        self.setWindowTitle("RedTeam AI")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 820)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Nav Rail ──────────────────────────────────────────────────────
        self._nav_rail = NavRail()
        main_layout.addWidget(self._nav_rail)

        # ── Module Stack + AI Panel ────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Module stacks
        self._stack = QStackedWidget()
        self._dashboard   = DashboardModule()
        self._targets     = TargetManagerModule()
        self._recon       = ReconModule()
        self._web_scan    = WebScanModule()
        self._exploitation = ExploitationModule()
        self._ctf         = CTFModule()
        self._reporting   = ReportingModule()
        self._settings    = SettingsModule(self.app_state.settings)

        for module in [self._dashboard, self._targets, self._recon, self._web_scan,
                       self._exploitation, self._ctf, self._reporting, self._settings]:
            self._stack.addWidget(module)

        # AI Chat Panel
        self._ai_panel = AIChatPanel()

        splitter.addWidget(self._stack)
        splitter.addWidget(self._ai_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([980, 380])

        main_layout.addWidget(splitter, 1)

        # ── Status Bar ────────────────────────────────────────────────────
        self._status_bar = AppStatusBar()
        self.setStatusBar(self._status_bar)

        # Update dashboard stats
        self._update_dashboard_stats()

    def _setup_shortcuts(self) -> None:
        # Ctrl+K command palette (stub)
        QShortcut(QKeySequence("Ctrl+K"), self).activated.connect(self._cmd_palette)
        QShortcut(QKeySequence("Ctrl+,"), self).activated.connect(lambda: self._navigate("settings"))

    def _setup_connections(self) -> None:
        # Nav rail
        self._nav_rail.module_changed.connect(self._navigate)

        # Dashboard
        self._dashboard.module_navigate.connect(self._navigate)

        # Targets
        self._targets.scan_requested.connect(self._handle_scan_from_target)

        # Recon module
        self._recon.run_tool.connect(self._run_tool)
        self._recon.ask_ai.connect(self._send_to_ai)
        self._recon.save_to_project.connect(self._save_output_to_project)

        # Web scan
        self._web_scan.run_tool.connect(self._run_tool)
        self._web_scan.ask_ai.connect(self._send_to_ai)
        self._web_scan.save_to_project.connect(self._save_output_to_project)

        # Exploitation
        self._exploitation.run_tool.connect(self._run_tool)
        self._exploitation.ask_ai.connect(self._send_to_ai)

        # CTF
        self._ctf.ask_ai.connect(self._send_to_ai)

        # Reporting
        self._reporting.ask_ai.connect(self._send_to_ai)
        self._reporting.generate_report.connect(self._generate_report)

        # Settings
        self._settings.settings_changed.connect(self._on_settings_changed)
        self._settings.health_check_requested.connect(self._health_check)

        # AI Panel
        self._ai_panel.send_requested.connect(self._send_to_ai)
        self._ai_panel.connect_stop(self._stop_ai)

    # ── Navigation ────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _navigate(self, module: str) -> None:
        module_map = {
            "dashboard":    0,
            "targets":      1,
            "recon":        2,
            "web_scan":     3,
            "exploitation": 4,
            "ctf":          5,
            "reporting":    6,
            "settings":     7,
        }
        idx = module_map.get(module, 0)
        self._stack.setCurrentIndex(idx)
        self._nav_rail.set_active(module)
        self.app_state.active_module = module

    # ── Tool Execution ────────────────────────────────────────────────────

    @pyqtSlot(str, dict)
    def _run_tool(self, tool_name: str, kwargs: dict) -> None:
        tool = self._registry.get_tool(tool_name)
        if not tool:
            self._status_bar.set_status(f"Tool '{tool_name}' not found")
            return

        if not self._registry.is_available(tool_name):
            hint = self._registry.get_hint(tool_name)
            msg = f"[{tool.display_name}] Not installed or not found in PATH.\n{hint}"
            self._show_tool_output(tool_name, msg)
            self._status_bar.set_status(f"{tool.display_name} not available")
            return

        # For built-in tools (CTF), run inline
        if tool.is_builtin:
            result = self._registry.execute(tool_name, **kwargs)
            self._show_tool_output(tool_name, result.output or result.error)
            return

        # Build command for subprocess
        cmd = tool.get_command(**kwargs)
        if not cmd:
            # Fallback: run via executor
            result = self._registry.execute(tool_name, **kwargs)
            self._show_tool_output(tool_name, result.output or result.error)
            return

        # Confirm for dangerous tools
        if tool.is_dangerous and self.app_state.settings.require_confirm_dangerous:
            cmd_str = " ".join(cmd)
            if not ConfirmDialog.ask(tool.display_name, cmd_str, self):
                return

        self._start_tool_worker(tool_name, cmd)

    def _start_tool_worker(self, tool_name: str, cmd: list[str]) -> None:
        if self._tool_worker and self._tool_worker.isRunning():
            self._tool_worker.stop()

        self._tool_output_buffer = ""
        self._tool_worker = ToolWorker(cmd)
        self._tool_worker.signals.output_line.connect(self._on_tool_line)
        self._tool_worker.signals.finished.connect(lambda code, out: self._on_tool_finished(tool_name, code, out))
        self._tool_worker.signals.error.connect(self._on_tool_error)
        self._tool_worker.start()

        self._status_bar.set_tool_busy(True, tool_name)
        self.app_state.tool_busy = True

        # Show output in active module
        active = self.app_state.active_module
        if active == "recon":
            self._recon.set_tool_busy(True, tool_name)
            self._recon.append_output(f"$ {' '.join(cmd)}\n")
        elif active == "web_scan":
            self._web_scan.set_tool_busy(True, tool_name)
            self._web_scan.append_output(f"$ {' '.join(cmd)}\n")

    @pyqtSlot(str)
    def _on_tool_line(self, line: str) -> None:
        self._tool_output_buffer += line + "\n"
        active = self.app_state.active_module
        if active == "recon":
            self._recon.append_output(line)
        elif active == "web_scan":
            self._web_scan.append_output(line)
        elif active == "exploitation":
            self._exploitation.append_output(line)

    @pyqtSlot(str, int, str)
    def _on_tool_finished(self, tool_name: str, exit_code: int, full_output: str) -> None:
        self._status_bar.set_tool_busy(False)
        self.app_state.tool_busy = False

        active = self.app_state.active_module
        if active == "recon":
            self._recon.set_tool_busy(False)
            color = "#3fb950" if exit_code == 0 else "#f85149"
            self._recon.append_output(f"\n[{tool_name} completed with exit code {exit_code}]")
        elif active == "web_scan":
            self._web_scan.set_tool_busy(False)
            self._web_scan.append_output(f"\n[{tool_name} completed with exit code {exit_code}]")

        # CVE lookup result goes to exploitation output
        if tool_name == "cve_lookup":
            self._exploitation.set_output(full_output)

    @pyqtSlot(str)
    def _on_tool_error(self, error: str) -> None:
        self._status_bar.set_tool_busy(False)
        self._status_bar.set_status(f"Tool error: {error}")
        self.app_state.tool_busy = False

    def _show_tool_output(self, tool_name: str, output: str) -> None:
        """Show output from a built-in / sync tool."""
        active = self.app_state.active_module
        if active == "recon":
            self._recon.append_output(output)
        elif active == "web_scan":
            self._web_scan.append_output(output)
        elif active == "exploitation":
            if tool_name == "cve_lookup":
                self._exploitation.set_output(output)
            else:
                self._exploitation.append_output(output)

    # ── AI Agent ──────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _send_to_ai(self, message: str) -> None:
        if self.app_state.ai_busy:
            return

        self.app_state.ai_busy = True
        self._status_bar.set_ai_busy(True)
        self._ai_panel.set_busy(True)
        self._ai_panel.add_user_message(message)
        self._ai_panel.begin_ai_response()

        # Build agent
        backend = create_backend(self.app_state.settings)
        history = MessageHistory(
            system_prompt=get_prompt(self.app_state.active_module),
            max_tokens=self.app_state.settings.max_agent_iterations * 800,
        )
        agent = RedTeamAgent(
            backend=backend,
            tool_executor=self._registry.execute_from_ai,
            tools_manifest=self._registry.get_manifest(),
            history=history,
            max_iterations=self.app_state.settings.max_agent_iterations,
            require_confirm_dangerous=self.app_state.settings.require_confirm_dangerous,
        )

        self._ai_worker = AIWorker(agent, message)
        self._ai_worker.signals.text_chunk.connect(self._on_ai_chunk)
        self._ai_worker.signals.tool_call.connect(self._on_ai_tool_call)
        self._ai_worker.signals.tool_result.connect(self._on_ai_tool_result)
        self._ai_worker.signals.confirm_required.connect(self._on_confirm_required)
        self._ai_worker.signals.done.connect(self._on_ai_done)
        self._ai_worker.signals.error.connect(self._on_ai_error)
        self._ai_worker.start()

    @pyqtSlot(str)
    def _on_ai_chunk(self, text: str) -> None:
        self._ai_panel.append_ai_chunk(text)

    @pyqtSlot(str, dict)
    def _on_ai_tool_call(self, tool_name: str, args: dict) -> None:
        self._current_tool_bubble = self._ai_panel.add_tool_call(tool_name, args)

    @pyqtSlot(str, str, bool)
    def _on_ai_tool_result(self, tool_name: str, output: str, error: bool) -> None:
        self._ai_panel.update_tool_result(output, error)
        # Also show in module terminal
        self._show_tool_output(tool_name, output)

    @pyqtSlot(object)
    def _on_confirm_required(self, event) -> None:
        confirmed = ConfirmDialog.ask(event.tool_name, event.command, self)
        event.confirmed = confirmed
        event.confirm_event.set()

    @pyqtSlot(str, int)
    def _on_ai_done(self, final: str, iterations: int) -> None:
        self._ai_panel.finalize_ai_response(final)
        self._ai_panel.set_busy(False)
        self._status_bar.set_ai_busy(False)
        self._status_bar.set_status(f"AI done ({iterations} iteration{'s' if iterations != 1 else ''})")
        self.app_state.ai_busy = False

    @pyqtSlot(str)
    def _on_ai_error(self, error: str) -> None:
        self._ai_panel.finalize_ai_response(f"**Error:** {error}")
        self._ai_panel.set_busy(False)
        self._status_bar.set_ai_busy(False)
        self._status_bar.set_status(f"AI error: {error[:60]}")
        self.app_state.ai_busy = False

    def _stop_ai(self) -> None:
        if self._ai_worker:
            self._ai_worker.stop()
        self._ai_panel.set_busy(False)
        self._status_bar.set_ai_busy(False)
        self.app_state.ai_busy = False

    # ── Other handlers ────────────────────────────────────────────────────

    @pyqtSlot(str)
    def _handle_scan_from_target(self, target: str) -> None:
        self._navigate("recon")
        self._recon.set_target(target)

    @pyqtSlot(object)
    def _on_settings_changed(self, settings) -> None:
        self.app_state.settings = settings
        from redteamai.config.manager import save_config
        save_config(settings)
        self._setup_registry()
        self._update_status_bar_backend()
        self._status_bar.set_status("Settings saved")

    @pyqtSlot(str)
    def _health_check(self, backend_name: str) -> None:
        import asyncio
        from redteamai.ai.backend_factory import create_backend

        old_backend = self.app_state.settings.ai_backend
        self.app_state.settings.ai_backend = backend_name
        backend = create_backend(self.app_state.settings)
        self.app_state.settings.ai_backend = old_backend

        async def _check():
            return await backend.health_check()

        try:
            loop = asyncio.new_event_loop()
            ok, msg = loop.run_until_complete(_check())
            loop.close()
        except Exception as e:
            ok, msg = False, str(e)

        icon = "✅" if ok else "❌"
        QMessageBox.information(self, f"{backend_name} Health Check", f"{icon} {msg}")

    @pyqtSlot(str, str)
    def _generate_report(self, fmt: str, path: str) -> None:
        from redteamai.reporting.generator import generate_report
        findings = self._reporting._findings
        try:
            generate_report(findings, fmt, path)
            self._status_bar.set_status(f"Report saved: {path}")
            QMessageBox.information(self, "Report Generated", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Report Error", str(e))

    @pyqtSlot(str, str)
    def _save_output_to_project(self, label: str, content: str) -> None:
        self._status_bar.set_status(f"Saved: {label}")

    def _cmd_palette(self) -> None:
        self._status_bar.set_status("Command palette: Ctrl+K  (navigate with nav rail)")

    def _update_dashboard_stats(self) -> None:
        available_tools = sum(1 for t in self._registry.list_tools() if t["available"])
        self._dashboard.update_stats(tools=available_tools)

    def _update_status_bar_backend(self) -> None:
        backend_name = self.app_state.settings.ai_backend
        self._status_bar.set_backend(backend_name, True)

    def closeEvent(self, event) -> None:
        if self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.stop()
        if self._tool_worker and self._tool_worker.isRunning():
            self._tool_worker.stop()
        event.accept()
