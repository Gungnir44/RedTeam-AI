# 🔴 RedTeam AI

> **AI-powered standalone desktop application for authorized penetration testing, CTF competitions, and home labs.**

![GitHub Dark Theme](https://img.shields.io/badge/theme-GitHub%20Dark-0d1117?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

---

## ⚠️ Legal Notice

**This tool is for authorized security testing only.** Always obtain explicit written permission before testing any system you do not own. The authors are not responsible for misuse.

---

## Features

- **🤖 AI Agent** — ReAct loop (Reasoning + Acting) with multiple free/paid backends
  - **Ollama** (free, local, default) — llama3.1, qwen2.5, mistral, etc.
  - **Groq** (free tier, very fast)
  - **Anthropic** (Claude)
  - **Any OpenAI-compatible** endpoint (LM Studio, Together.ai, etc.)

- **🔍 Reconnaissance** — Nmap, Whois, Dig, theHarvester, Subfinder
- **🌐 Web Scanning** — Gobuster, ffuf, Nikto, WhatWeb
- **💥 Exploitation** — SearchSploit, CVE lookup (NVD), Metasploit RPC
- **🚩 CTF Solver** — Base64, Hex, ROT13, Caesar, XOR, Morse, Atbash, Hash ID, and more
- **📋 Reporting** — Markdown, HTML, and PDF report generation
- **🎯 Target Manager** — Track hosts, ports, services with SQLite storage

---

## Installation

```bash
# Clone
git clone https://github.com/Gungnir44/RedTeam-AI.git
cd RedTeam-AI

# Install Python dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Ollama (Recommended Free AI Backend)

```bash
# Install Ollama: https://ollama.com
# Pull a model:
ollama pull llama3.1          # 8B — good balance
ollama pull qwen2.5:7b        # Alternative
ollama pull mistral:7b        # Fast
```

---

## Quick Start

1. Launch: `python main.py`
2. **Settings** → Select AI backend (Ollama is default, click Health Check)
3. **Targets** → Add your authorized target
4. **Recon** → Run Nmap scan
5. **AI Panel** → Ask "What did the scan find? What should I try next?"
6. **Reporting** → Generate PDF/Markdown report

---

## Requirements

- Python 3.10+
- PyQt6
- Ollama (for free local AI) OR API key for Groq/Anthropic/OpenAI

**Optional tools** (greyed out with install hints if missing):
- `nmap`, `whois`, `dig`, `gobuster`, `ffuf`, `nikto`, `whatweb`
- `theHarvester`, `subfinder`, `searchsploit`

---

## Architecture

```
RedTeamAI/
├── main.py                    # Entry point
├── redteamai/
│   ├── ai/                    # AI backends + ReAct agent
│   ├── tools/adapters/        # Tool wrappers (Nmap, Gobuster, etc.)
│   ├── gui/                   # PyQt6 UI (dark theme, modules, panels)
│   ├── data/                  # SQLAlchemy models + repositories
│   ├── workers/               # QThread bridges (AI, tools)
│   ├── reporting/             # MD/HTML/PDF report generation
│   └── utils/                 # Logger, ANSI parser, sanitizer, etc.
└── assets/                    # Icons, fonts
```

---

## Building Standalone Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name RedTeamAI main.py
```

Or use GitHub Actions (`.github/workflows/build.yml`) — produces Windows EXE + Linux binary on tag push.

---

## License

MIT — See [LICENSE](LICENSE)
