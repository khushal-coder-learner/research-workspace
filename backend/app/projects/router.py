from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import DBSession
from app.projects.models import Project
from app.projects.schemas import ProjectCreate, ProjectRead
from app.projects.service import (
    ProjectNotFoundError,
    create_project,
    get_project,
    list_projects,
)

router = APIRouter(tags=["projects"])


def _map_project_error(exception: ProjectNotFoundError) -> HTTPException:
    if isinstance(exception, ProjectNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project_route(
    project_data: ProjectCreate,
    db: DBSession,
) -> Project:
    return create_project(db, project_data)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects_route(db: DBSession) -> list[Project]:
    return list_projects(db)


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project_route(project_id: UUID, db: DBSession) -> Project:
    try:
        return get_project(db, project_id)
    except ProjectNotFoundError as exception:
        raise _map_project_error(exception) from exception
