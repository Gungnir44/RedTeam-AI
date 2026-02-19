"""Application-wide constants: colors, paths, version."""
from pathlib import Path

# ── Version ──────────────────────────────────────────────────────────────────
APP_NAME = "RedTeam AI"
APP_VERSION = "0.1.0"
APP_AUTHOR = "RedTeam AI Project"
APP_URL = "https://github.com/your-org/redteamai"

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
FONTS_DIR = ASSETS_DIR / "fonts"
STYLES_DIR = ROOT_DIR / "redteamai" / "gui" / "styles"

import sys, os
if sys.platform == "win32":
    APP_DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / "RedTeamAI"
else:
    APP_DATA_DIR = Path.home() / ".local" / "share" / "RedTeamAI"

CONFIG_FILE = APP_DATA_DIR / "config.toml"
DB_FILE = APP_DATA_DIR / "redteamai.db"
LOG_FILE = APP_DATA_DIR / "redteamai.log"
PROJECTS_DIR = APP_DATA_DIR / "projects"

# ── GitHub Dark Palette ───────────────────────────────────────────────────────
COLOR_BG           = "#0d1117"   # Main window background
COLOR_SURFACE      = "#161b22"   # Cards, panels
COLOR_SURFACE2     = "#21262d"   # Elevated surfaces
COLOR_BORDER       = "#30363d"   # Borders, dividers
COLOR_BORDER_LIGHT = "#484f58"   # Lighter borders
COLOR_ACCENT       = "#1f6feb"   # Primary blue (interactive)
COLOR_ACCENT_HOVER = "#388bfd"   # Hover state
COLOR_SUCCESS      = "#3fb950"   # Green
COLOR_WARNING      = "#d29922"   # Yellow
COLOR_DANGER       = "#f85149"   # Red
COLOR_INFO         = "#58a6ff"   # Light blue
COLOR_TEXT         = "#c9d1d9"   # Primary text
COLOR_TEXT_MUTED   = "#8b949e"   # Secondary text
COLOR_TEXT_SUBTLE  = "#6e7681"   # Tertiary text
COLOR_LINK         = "#58a6ff"   # Link text

# ── Terminal Colors ───────────────────────────────────────────────────────────
COLOR_TERM_BG      = "#0d1117"
COLOR_TERM_FG      = "#00ff41"   # Matrix green
COLOR_TERM_CURSOR  = "#00ff41"

# ── Severity Colors ───────────────────────────────────────────────────────────
SEVERITY_COLORS = {
    "critical": "#ff0000",
    "high":     "#f85149",
    "medium":   "#d29922",
    "low":      "#3fb950",
    "info":     "#58a6ff",
}

# ── UI Dimensions ─────────────────────────────────────────────────────────────
NAV_RAIL_COLLAPSED = 64
NAV_RAIL_EXPANDED  = 200
AI_PANEL_MIN_WIDTH = 320
AI_PANEL_DEFAULT   = 380
STATUS_BAR_HEIGHT  = 28
TITLE_BAR_HEIGHT   = 36

# ── AI Defaults ───────────────────────────────────────────────────────────────
DEFAULT_OLLAMA_HOST   = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL  = "llama3.1:8b"
DEFAULT_GROQ_MODEL    = "llama3-70b-8192"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_OPENAI_MODEL  = "gpt-4o-mini"
MAX_AGENT_ITERATIONS  = 10
MAX_HISTORY_TOKENS    = 8000

# ── Keyboard Shortcuts ────────────────────────────────────────────────────────
SHORTCUT_SEND_AI     = "Ctrl+Return"
SHORTCUT_CMD_PALETTE = "Ctrl+K"
SHORTCUT_NEW_TARGET  = "Ctrl+T"
SHORTCUT_SETTINGS    = "Ctrl+,"
