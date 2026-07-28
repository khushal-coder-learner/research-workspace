from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.core.exceptions import ProjectNotFoundError
from app.projects.models import Project
from app.projects.schemas import ProjectCreate
from app.projects.service import create_project, get_project, list_projects


PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_create_project_persists_and_returns_project() -> None:
    # Arrange
    session = MagicMock()
    project_data = ProjectCreate(name="Research", description="Papers")

    # Act
    project = create_project(session, project_data)

    # Assert
    assert project.name == "Research"
    assert project.description == "Papers"
    session.add.assert_called_once_with(project)
    session.commit.assert_called_once_with()
    session.refresh.assert_called_once_with(project)


def test_create_project_rolls_back_when_commit_fails() -> None:
    # Arrange
    session = MagicMock()
    session.commit.side_effect = RuntimeError("database unavailable")

    # Act / Assert
    with pytest.raises(RuntimeError, match="database unavailable"):
        create_project(session, ProjectCreate(name="Research"))

    session.rollback.assert_called_once_with()
    session.refresh.assert_not_called()


def test_list_projects_returns_database_ordered_results() -> None:
    # Arrange
    session = MagicMock()
    projects = [Project(id=PROJECT_ID, name="Research")]
    session.scalars.return_value.all.return_value = projects

    # Act
    result = list_projects(session)

    # Assert
    assert result == projects
    session.scalars.assert_called_once()


def test_get_project_returns_existing_project() -> None:
    # Arrange
    session = MagicMock()
    project = Project(id=PROJECT_ID, name="Research")
    session.scalar.return_value = project

    # Act
    result = get_project(session, PROJECT_ID)

    # Assert
    assert result is project
    session.scalar.assert_called_once()


def test_get_project_raises_when_project_does_not_exist() -> None:
    # Arrange
    session = MagicMock()
    session.scalar.return_value = None

    # Act / Assert
    with pytest.raises(ProjectNotFoundError):
        get_project(session, PROJECT_ID)
