from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.core.exceptions import ProjectNotFoundError
from app.projects.models import Project
from app.retrieval.service import RetrievalService


PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_retrieve_validates_project_and_delegates_to_retriever() -> None:
    # Arrange
    session = MagicMock()
    retriever = MagicMock()
    session.get.return_value = Project(id=PROJECT_ID, name="Research")
    retriever.retrieve.return_value = ["node"]
    service = RetrievalService(session, retriever)

    # Act
    result = service.retrieve("What is attention?", project_id=PROJECT_ID, top_k=5)

    # Assert
    assert result == ["node"]
    retriever.retrieve.assert_called_once_with(
        query="What is attention?", project_id=PROJECT_ID, top_k=5
    )


def test_retrieve_raises_when_project_is_missing() -> None:
    # Arrange
    session = MagicMock()
    retriever = MagicMock()
    session.get.return_value = None
    service = RetrievalService(session, retriever)

    # Act / Assert
    with pytest.raises(ProjectNotFoundError):
        service.retrieve("question", project_id=PROJECT_ID, top_k=5)

    retriever.retrieve.assert_not_called()


def test_retrieve_propagates_retriever_failure() -> None:
    # Arrange
    session = MagicMock()
    retriever = MagicMock()
    session.get.return_value = Project(id=PROJECT_ID, name="Research")
    retriever.retrieve.side_effect = RuntimeError("vector store unavailable")
    service = RetrievalService(session, retriever)

    # Act / Assert
    with pytest.raises(RuntimeError, match="vector store unavailable"):
        service.retrieve("question", project_id=PROJECT_ID, top_k=5)
