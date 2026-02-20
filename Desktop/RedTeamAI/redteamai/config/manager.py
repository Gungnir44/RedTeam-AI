"""Load/save config.toml using tomlkit for round-trip preservation."""
from __future__ import annotations
import tomlkit
from pathlib import Path
from typing import Any
from redteamai.constants import CONFIG_FILE, APP_DATA_DIR
from redteamai.config.settings import AppSettings


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config() -> AppSettings:
    """Load config from TOML file, falling back to defaults."""
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        try:
            raw = tomlkit.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Convert tomlkit tables to plain dicts so pydantic can coerce nested models
            plain = _toml_to_plain_dict(raw)
            return AppSettings(**plain)
        except Exception:
            pass

    # Write default config on first run
    settings = AppSettings()
    save_config(settings)
    return settings


def save_config(settings: AppSettings) -> None:
    """Persist settings to TOML file."""
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = settings.model_dump()
    doc = _build_toml_doc(data)
    CONFIG_FILE.write_text(tomlkit.dumps(doc), encoding="utf-8")


def _toml_to_plain_dict(d) -> dict:
    """Recursively convert a tomlkit document/table to a plain Python dict."""
    result = {}
    for k, v in d.items():
        if hasattr(v, "items"):
            result[k] = _toml_to_plain_dict(v)
        else:
            result[k] = v
    return result


def _build_toml_doc(data: dict) -> tomlkit.TOMLDocument:
    """Build a tomlkit document from a flat or nested dict."""
    doc = tomlkit.document()
    for k, v in data.items():
        if isinstance(v, dict):
            table = tomlkit.table()
            for sk, sv in v.items():
                table.add(sk, sv)
            doc.add(k, table)
        else:
            doc.add(k, v)
    return doc
