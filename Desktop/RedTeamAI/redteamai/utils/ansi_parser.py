"""Convert ANSI escape codes to Qt-compatible color spans."""
from __future__ import annotations
import re
from typing import NamedTuple

_ANSI_RE = re.compile(r'\x1b\[([0-9;]*)m')

# Map ANSI color codes to hex colors (GitHub dark palette)
_FG_COLORS = {
    30: "#21262d",  # Black → dark surface
    31: "#f85149",  # Red
    32: "#3fb950",  # Green
    33: "#d29922",  # Yellow
    34: "#58a6ff",  # Blue
    35: "#bc8cff",  # Magenta
    36: "#39c5cf",  # Cyan
    37: "#c9d1d9",  # White
    90: "#6e7681",  # Bright black / gray
    91: "#ff6e6e",  # Bright red
    92: "#56d364",  # Bright green
    93: "#e3b341",  # Bright yellow
    94: "#79c0ff",  # Bright blue
    95: "#d2a8ff",  # Bright magenta
    96: "#56d9ed",  # Bright cyan
    97: "#f0f6fc",  # Bright white
}

_BG_COLORS = {c + 10: v for c, v in _FG_COLORS.items()}


class Span(NamedTuple):
    text: str
    fg: str | None
    bg: str | None
    bold: bool
    italic: bool


def parse_ansi(text: str) -> list[Span]:
    """Parse ANSI-colored text into a list of styled spans."""
    spans: list[Span] = []
    fg = None
    bg = None
    bold = False
    italic = False
    pos = 0

    for m in _ANSI_RE.finditer(text):
        # Emit plain text before this escape
        if m.start() > pos:
            spans.append(Span(text[pos:m.start()], fg, bg, bold, italic))
        pos = m.end()

        # Parse codes
        codes_str = m.group(1)
        if not codes_str:
            codes = [0]
        else:
            codes = [int(c) for c in codes_str.split(";") if c]

        for code in codes:
            if code == 0:
                fg = bg = None
                bold = italic = False
            elif code == 1:
                bold = True
            elif code == 3:
                italic = True
            elif code == 22:
                bold = False
            elif code == 23:
                italic = False
            elif code in _FG_COLORS:
                fg = _FG_COLORS[code]
            elif code in _BG_COLORS:
                bg = _BG_COLORS[code]

    # Emit remaining text
    if pos < len(text):
        spans.append(Span(text[pos:], fg, bg, bold, italic))

    return spans


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape codes from text."""
    return _ANSI_RE.sub("", text)


def ansi_to_html(text: str) -> str:
    """Convert ANSI text to simple HTML spans for display."""
    spans = parse_ansi(text)
    parts = []
    for span in spans:
        if not span.text:
            continue
        style_parts = []
        if span.fg:
            style_parts.append(f"color:{span.fg}")
        if span.bg:
            style_parts.append(f"background-color:{span.bg}")
        if span.bold:
            style_parts.append("font-weight:bold")
        if span.italic:
            style_parts.append("font-style:italic")

        escaped = span.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if style_parts:
            parts.append(f'<span style="{";".join(style_parts)}">{escaped}</span>')
        else:
            parts.append(escaped)
    return "".join(parts)
