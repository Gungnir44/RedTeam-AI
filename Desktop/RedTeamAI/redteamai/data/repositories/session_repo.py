"""CRUD operations for Sessions and Messages."""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from redteamai.data.models import Session, Message


def create_session(db: DBSession, project_id: int, name: str = "New Session", module: str = "chat") -> Session:
    session = Session(project_id=project_id, name=name, module=module)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_by_id(db: DBSession, session_id: int) -> Optional[Session]:
    return db.get(Session, session_id)


def list_sessions(db: DBSession, project_id: int) -> list[Session]:
    return db.query(Session).filter(Session.project_id == project_id).order_by(Session.updated_at.desc()).all()


def add_message(db: DBSession, session_id: int, role: str, content: str, **kwargs) -> Message:
    msg = Message(session_id=session_id, role=role, content=content, **kwargs)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: DBSession, session_id: int) -> list[Message]:
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
