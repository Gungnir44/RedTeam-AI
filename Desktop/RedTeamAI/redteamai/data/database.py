"""Database engine initialization and session factory."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from redteamai.data.models import Base


_engine = None
_SessionLocal = None


def init_db(db_path: Path | None = None) -> None:
    """Initialize the SQLite database engine and create tables."""
    global _engine, _SessionLocal
    if db_path is None:
        from redteamai.constants import DB_FILE
        db_path = DB_FILE
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"
    _engine = create_engine(url, connect_args={"check_same_thread": False}, echo=False)

    # Enable WAL for better concurrency
    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(conn, _record):
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def get_session() -> Session:
    """Return a new SQLAlchemy session. Caller is responsible for closing."""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


def get_engine():
    if _engine is None:
        init_db()
    return _engine
