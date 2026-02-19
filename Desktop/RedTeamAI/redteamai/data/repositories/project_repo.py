"""CRUD operations for Projects."""
from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from redteamai.data.models import Project


def create_project(db: Session, name: str, description: str = "", scope: str = "") -> Project:
    project = Project(name=name, description=description, scope=scope)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    return db.get(Project, project_id)


def list_projects(db: Session) -> list[Project]:
    return db.query(Project).filter(Project.is_active == True).order_by(Project.updated_at.desc()).all()


def update_project(db: Session, project_id: int, **kwargs) -> Optional[Project]:
    project = db.get(Project, project_id)
    if project:
        for k, v in kwargs.items():
            setattr(project, k, v)
        db.commit()
        db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = db.get(Project, project_id)
    if project:
        project.is_active = False
        db.commit()
        return True
    return False
