"""AI Chat Panel — streaming markdown chat with tool call display."""
from __future__ import annotations
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QTextEdit, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QTextCursor, QColor


class MessageBubble(QFrame):
    """Single chat message bubble."""

    def __init__(self, role: str, content: str = "", parent=None):
        super().__init__(parent)
        self._role = role

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Role label
        role_lbl = QLabel("You" if role == "user" else "🤖 RedTeam AI")
        role_lbl.setStyleSheet(
            f"font-size:11px; font-weight:bold; color:{'#58a6ff' if role == 'user' else '#3fb950'}; background:transparent;"
        )
        layout.addWidget(role_lbl)

        # Content
        self._content_label = QLabel(content)
        self._content_label.setWordWrap(True)
        self._content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self._content_label.setOpenExternalLinks(True)
        layout.addWidget(self._content_label)

        # Style based on role
        if role == "user":
            self.setStyleSheet("background:#1f3a6e; border:1px solid #1f6feb; border-radius:8px;")
        elif role == "tool":
            self.setStyleSheet("background:#0f2d1a; border:1px solid #3fb950; border-radius:8px;")
        else:
            self.setStyleSheet("background:#161b22; border:1px solid #30363d; border-radius:8px;")

    def set_content(self, content: str) -> None:
        """Update content — converts simple markdown to HTML."""
        html = _md_to_html(content)
        self._content_label.setText(html)

    def append_text(self, text: str) -> None:
        """Append streamed text."""
        current = self._content_label.text()
        self._content_label.setText(current + text)


class ToolCallBubble(QFrame):
    """Displays a tool call and its result."""

    def __init__(self, tool_name: str, args: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#1a1a2e; border:1px solid #1f6feb; border-radius:8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        header = QLabel(f"🔧 Tool: {tool_name}")
        header.setStyleSheet("font-size:11px; font-weight:bold; color:#1f6feb; background:transparent;")

        args_text = "\n".join(f"  {k}: {v}" for k, v in args.items())
        args_lbl = QLabel(f"<pre style='color:#8b949e;margin:0;'>{args_text}</pre>")
        args_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._result_lbl = QLabel("Running…")
        self._result_lbl.setWordWrap(True)
        self._result_lbl.setObjectName("muted")
        self._result_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        layout.addWidget(header)
        layout.addWidget(args_lbl)
        layout.addWidget(self._result_lbl)

    def set_result(self, output: str, error: bool = False) -> None:
        color = "#f85149" if error else "#3fb950"
        truncated = output[:500] + ("…" if len(output) > 500 else "")
        self._result_lbl.setText(f"<pre style='color:{color};font-size:11px;margin:0;'>{_escape(truncated)}</pre>")


class AIChatPanel(QWidget):
    """Right-side AI chat panel with streaming markdown rendering."""

    send_requested = pyqtSignal(str)
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("aiPanel")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background:#161b22; border-bottom:1px solid #30363d;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 8, 12, 8)

        title = QLabel("🤖 AI Assistant")
        title.setStyleSheet("font-weight:bold; color:#c9d1d9; background:transparent;")

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(60, 24)
        clear_btn.setStyleSheet("font-size:11px; padding:2px 6px;")
        clear_btn.clicked.connect(self._clear_chat)

        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(clear_btn)

        # Scrollable message area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { border:none; background:#0d1117; }")

        self._msg_container = QWidget()
        self._msg_container.setStyleSheet("background:#0d1117;")
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setContentsMargins(8, 8, 8, 8)
        self._msg_layout.setSpacing(8)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_container)

        # Input area
        input_area = QWidget()
        input_area.setStyleSheet("background:#161b22; border-top:1px solid #30363d;")
        il = QVBoxLayout(input_area)
        il.setContentsMargins(8, 8, 8, 8)
        il.setSpacing(6)

        self._input = QPlainTextEdit()
        self._input.setObjectName("chatInput")
        self._input.setPlaceholderText("Ask the AI… (Ctrl+Enter to send)")
        self._input.setMaximumHeight(100)

        send_row = QHBoxLayout()
        self._send_btn = QPushButton("Send  ↵")
        self._send_btn.setObjectName("primary")
        self._send_btn.setFixedHeight(32)
        self._send_btn.clicked.connect(self._send)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("danger")
        self._stop_btn.setFixedHeight(32)
        self._stop_btn.setEnabled(False)

        send_row.addWidget(self._stop_btn)
        send_row.addStretch()
        send_row.addWidget(self._send_btn)

        il.addWidget(self._input)
        il.addLayout(send_row)

        layout.addWidget(header)
        layout.addWidget(self._scroll, 1)
        layout.addWidget(input_area)

        # Shortcut: Ctrl+Enter to send
        self._shortcut = QShortcut(QKeySequence("Ctrl+Return"), self._input)
        self._shortcut.activated.connect(self._send)

        self._current_ai_bubble: MessageBubble | None = None
        self._current_tool_bubble: ToolCallBubble | None = None

    # ── Public API ────────────────────────────────────────────────────────────

    def add_user_message(self, text: str) -> None:
        bubble = MessageBubble("user", text)
        self._insert_bubble(bubble)
        self._scroll_to_bottom()

    def begin_ai_response(self) -> None:
        """Start a new AI response bubble (for streaming)."""
        self._current_ai_bubble = MessageBubble("assistant", "")
        self._insert_bubble(self._current_ai_bubble)

    def append_ai_chunk(self, text: str) -> None:
        if self._current_ai_bubble:
            self._current_ai_bubble.append_text(text)
            self._scroll_to_bottom()

    def finalize_ai_response(self, full_text: str) -> None:
        if self._current_ai_bubble:
            self._current_ai_bubble.set_content(full_text)
            self._current_ai_bubble = None
        self._scroll_to_bottom()

    def add_tool_call(self, tool_name: str, args: dict) -> ToolCallBubble:
        bubble = ToolCallBubble(tool_name, args)
        self._insert_bubble(bubble)
        self._current_tool_bubble = bubble
        self._scroll_to_bottom()
        return bubble

    def update_tool_result(self, output: str, error: bool = False) -> None:
        if self._current_tool_bubble:
            self._current_tool_bubble.set_result(output, error)
            self._current_tool_bubble = None
        self._scroll_to_bottom()

    def set_busy(self, busy: bool) -> None:
        self._send_btn.setEnabled(not busy)
        self._stop_btn.setEnabled(busy)
        self._input.setReadOnly(busy)

    def connect_stop(self, slot) -> None:
        self._stop_btn.clicked.connect(slot)

    # ── Internal ─────────────────────────────────────────────────────────────

    def _send(self) -> None:
        text = self._input.toPlainText().strip()
        if text:
            self._input.clear()
            self.send_requested.emit(text)

    def _clear_chat(self) -> None:
        while self._msg_layout.count() > 1:  # Keep the stretch
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.clear_requested.emit()

    def _insert_bubble(self, widget: QWidget) -> None:
        # Insert before the stretch item
        self._msg_layout.insertWidget(self._msg_layout.count() - 1, widget)

    def _scroll_to_bottom(self) -> None:
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())


def _md_to_html(text: str) -> str:
    """Convert basic markdown to HTML for QLabel display."""
    # Code blocks
    text = re.sub(r'```(?:\w+)?\n(.*?)```', lambda m: f'<pre style="background:#161b22;padding:6px;border-radius:4px;color:#c9d1d9;">{_escape(m.group(1))}</pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', lambda m: f'<code style="background:#21262d;padding:1px 4px;border-radius:3px;">{_escape(m.group(1))}</code>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#58a6ff;">\1</a>', text)
    # Line breaks
    text = text.replace("\n", "<br>")
    return f'<span style="color:#c9d1d9;font-size:13px;">{text}</span>'


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
