from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.projects.models import Project
from app.projects.schemas import ProjectCreate
from app.core.exceptions import ProjectNotFoundError


def create_project(session: Session, project_data: ProjectCreate) -> Project:
    project = Project(
        name=project_data.name,
        description=project_data.description,
    )
    try:
        session.add(project)
        session.commit()
        session.refresh(project)
    except Exception:
        session.rollback()
        raise
    return project


def list_projects(session: Session) -> list[Project]:
    statement = select(Project).order_by(Project.created_at.desc())
    return list(session.scalars(statement).all())


def get_project(session: Session, project_id: UUID) -> Project:
    statement = select(Project).where(Project.id == project_id)
    project = session.scalar(statement)

    if project is None:
        raise ProjectNotFoundError

    return project
