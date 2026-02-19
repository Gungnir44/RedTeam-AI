"""Application-wide logging setup."""
from __future__ import annotations
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO", log_file: Path | None = None) -> None:
    """Configure root logger with console + optional file handler."""
    from redteamai.constants import LOG_FILE
    if log_file is None:
        log_file = LOG_FILE

    log_file.parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Rotating file handler (5 MB × 3 backups)
    try:
        fh = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        fh.setFormatter(formatter)
        root.addHandler(fh)
    except OSError:
        pass  # Non-fatal if log file can't be created


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
