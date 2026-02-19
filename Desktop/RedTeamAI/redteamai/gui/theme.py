"""Load QSS stylesheet and build QPalette."""
from __future__ import annotations
from pathlib import Path
from PyQt6.QtGui import QPalette, QColor, QFontDatabase, QFont
from PyQt6.QtWidgets import QApplication
from redteamai.constants import STYLES_DIR, FONTS_DIR, COLOR_BG, COLOR_TEXT


def _load_qss() -> str:
    qss_path = STYLES_DIR / "dark.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def _build_palette() -> QPalette:
    palette = QPalette()
    bg      = QColor("#0d1117")
    surface = QColor("#161b22")
    border  = QColor("#30363d")
    text    = QColor("#c9d1d9")
    muted   = QColor("#8b949e")
    accent  = QColor("#1f6feb")
    danger  = QColor("#f85149")
    success = QColor("#3fb950")
    warning = QColor("#d29922")

    palette.setColor(QPalette.ColorRole.Window,          bg)
    palette.setColor(QPalette.ColorRole.WindowText,      text)
    palette.setColor(QPalette.ColorRole.Base,            surface)
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1c2128"))
    palette.setColor(QPalette.ColorRole.Text,            text)
    palette.setColor(QPalette.ColorRole.BrightText,      QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Button,          surface)
    palette.setColor(QPalette.ColorRole.ButtonText,      text)
    palette.setColor(QPalette.ColorRole.Highlight,       accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link,            QColor("#58a6ff"))
    palette.setColor(QPalette.ColorRole.LinkVisited,     QColor("#bc8cff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     surface)
    palette.setColor(QPalette.ColorRole.ToolTipText,     text)
    palette.setColor(QPalette.ColorRole.PlaceholderText, muted)

    # Disabled
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, muted)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, muted)

    return palette


def _load_fonts() -> None:
    """Load bundled JetBrains Mono if available."""
    font_dir = FONTS_DIR
    if font_dir.exists():
        for ttf in font_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(ttf))


def apply_theme(app: QApplication) -> None:
    """Apply the dark theme to the QApplication."""
    _load_fonts()

    # Try to use JetBrains Mono, fall back gracefully
    font = QFont("JetBrains Mono", 13)
    if not font.exactMatch():
        for fallback in ("Cascadia Code", "Consolas", "Courier New"):
            font = QFont(fallback, 13)
            if font.exactMatch():
                break
    app.setFont(font)

    app.setPalette(_build_palette())

    qss = _load_qss()
    if qss:
        app.setStyleSheet(qss)
