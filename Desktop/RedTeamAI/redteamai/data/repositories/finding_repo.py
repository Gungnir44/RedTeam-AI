"""CRUD operations for Findings."""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from redteamai.data.models import Finding


def create_finding(db: Session, project_id: int, title: str, severity: str = "info", **kwargs) -> Finding:
    finding = Finding(project_id=project_id, title=title, severity=severity, **kwargs)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding


def get_finding(db: Session, finding_id: int) -> Optional[Finding]:
    return db.get(Finding, finding_id)


def list_findings(db: Session, project_id: int) -> list[Finding]:
    return db.query(Finding).filter(Finding.project_id == project_id).order_by(Finding.created_at.desc()).all()


def update_finding(db: Session, finding_id: int, **kwargs) -> Optional[Finding]:
    finding = db.get(Finding, finding_id)
    if finding:
        for k, v in kwargs.items():
            setattr(finding, k, v)
        db.commit()
        db.refresh(finding)
    return finding


def delete_finding(db: Session, finding_id: int) -> bool:
    finding = db.get(Finding, finding_id)
    if finding:
        db.delete(finding)
        db.commit()
        return True
    return False
