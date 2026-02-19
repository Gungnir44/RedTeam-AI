"""CTF Module — encoding/decoding and challenge solver."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal


OPERATIONS = [
    ("base64_decode",  "Base64 → Text"),
    ("base64_encode",  "Text → Base64"),
    ("hex_decode",     "Hex → Text"),
    ("hex_encode",     "Text → Hex"),
    ("rot13",          "ROT13"),
    ("caesar",         "Caesar Cipher"),
    ("xor",            "XOR Cipher"),
    ("morse_decode",   "Morse → Text"),
    ("morse_encode",   "Text → Morse"),
    ("binary_decode",  "Binary → Text"),
    ("binary_encode",  "Text → Binary"),
    ("url_decode",     "URL Decode"),
    ("url_encode",     "URL Encode"),
    ("atbash",         "Atbash"),
    ("hash_identify",  "Identify Hash"),
    ("hash_md5",       "MD5 Hash"),
    ("hash_sha256",    "SHA-256 Hash"),
    ("from_decimal",   "Decimal → Text"),
    ("to_decimal",     "Text → Decimal"),
]


class CTFModule(QWidget):
    run_tool = pyqtSignal(str, dict)
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
        title = QLabel("CTF Challenge Solver")
        title.setObjectName("heading")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(16)

        # Operation selector
        op_row = QHBoxLayout()
        op_label = QLabel("Operation:")
        self._op_combo = QComboBox()
        for op_id, op_label_text in OPERATIONS:
            self._op_combo.addItem(op_label_text, op_id)
        self._op_combo.setMinimumWidth(200)

        self._key_label = QLabel("Key:")
        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("Key (for XOR, Caesar shift)")
        self._key_input.setMaximumWidth(150)

        run_btn = QPushButton("▶  Decode / Encode")
        run_btn.setObjectName("primary")
        run_btn.clicked.connect(self._run_operation)

        self._ai_btn = QPushButton("🤖 Ask AI")
        self._ai_btn.clicked.connect(self._ask_ai_help)

        op_row.addWidget(op_label)
        op_row.addWidget(self._op_combo)
        op_row.addWidget(self._key_label)
        op_row.addWidget(self._key_input)
        op_row.addStretch()
        op_row.addWidget(self._ai_btn)
        op_row.addWidget(run_btn)

        content_layout.addLayout(op_row)

        # I/O area
        io_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Input
        input_group = QGroupBox("Input")
        input_lay = QVBoxLayout(input_group)
        self._input_text = QTextEdit()
        self._input_text.setPlaceholderText("Paste your encoded/encrypted text here…")
        self._input_text.setStyleSheet("background:#0d1117; color:#c9d1d9; border:none;")
        input_lay.addWidget(self._input_text)

        # Output
        output_group = QGroupBox("Output")
        output_lay = QVBoxLayout(output_group)
        output_btn_row = QHBoxLayout()
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(60)
        copy_btn.clicked.connect(self._copy_output)
        use_as_input_btn = QPushButton("Use as Input")
        use_as_input_btn.clicked.connect(self._use_as_input)
        output_btn_row.addStretch()
        output_btn_row.addWidget(copy_btn)
        output_btn_row.addWidget(use_as_input_btn)

        self._output_text = QTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setStyleSheet("background:#0d1117; color:#3fb950; border:none;")
        output_lay.addLayout(output_btn_row)
        output_lay.addWidget(self._output_text)

        io_splitter.addWidget(input_group)
        io_splitter.addWidget(output_group)
        content_layout.addWidget(io_splitter, 1)

        # Quick decode all (try all common encodings)
        quick_row = QHBoxLayout()
        auto_btn = QPushButton("🔮 Auto-Detect & Try All Encodings")
        auto_btn.clicked.connect(self._auto_decode)
        quick_row.addWidget(auto_btn)
        quick_row.addStretch()
        content_layout.addLayout(quick_row)

        layout.addWidget(content, 1)

        # Internal tool instance for builtin ops
        from redteamai.tools.adapters.builtin_ctf import BuiltinCTFTool
        self._ctf_tool = BuiltinCTFTool()

    def _run_operation(self) -> None:
        op = self._op_combo.currentData()
        text = self._input_text.toPlainText()
        key = self._key_input.text()
        if not text.strip():
            return
        result = self._ctf_tool.execute(operation=op, text=text, key=key)
        if result.success:
            self._output_text.setPlainText(result.output)
        else:
            self._output_text.setStyleSheet("background:#0d1117; color:#f85149; border:none;")
            self._output_text.setPlainText(f"Error: {result.error}")
            self._output_text.setStyleSheet("background:#0d1117; color:#3fb950; border:none;")

    def _auto_decode(self) -> None:
        text = self._input_text.toPlainText().strip()
        if not text:
            return
        results = []
        for op_id, op_name in OPERATIONS[:10]:  # Try first 10 (encode/decode)
            if "encode" in op_id:
                continue
            try:
                r = self._ctf_tool.execute(operation=op_id, text=text)
                if r.success and r.output and r.output != text:
                    results.append(f"[{op_name}]\n{r.output}\n")
            except Exception:
                pass
        self._output_text.setPlainText("\n".join(results) if results else "No successful decodings found.")

    def _copy_output(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._output_text.toPlainText())

    def _use_as_input(self) -> None:
        self._input_text.setPlainText(self._output_text.toPlainText())
        self._output_text.clear()

    def _ask_ai_help(self) -> None:
        text = self._input_text.toPlainText().strip()
        if text:
            self.ask_ai.emit(f"Help me decode/crack this CTF challenge text:\n```\n{text[:500]}\n```\nTry all common encodings and ciphers.")

    def set_input(self, text: str) -> None:
        self._input_text.setPlainText(text)
