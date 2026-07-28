from unittest.mock import MagicMock
from uuid import UUID

import pytest
from llama_index.core.base.response.schema import Response

from app.core.exceptions import ProjectNotFoundError
from app.core.config import settings
from app.projects.models import Project
from app.query.service import QueryService


PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_query_validates_project_and_delegates_to_query_engine() -> None:
    # Arrange
    session = MagicMock()
    query_engine = MagicMock()
    session.get.return_value = Project(id=PROJECT_ID, name="Research")
    query_engine.query.return_value = Response(response="answer", source_nodes=[])
    service = QueryService(session, query_engine)

    # Act
    result = service.query("question", project_id=PROJECT_ID)

    # Assert
    assert result.answer == "answer"
    query_engine.query.assert_called_once_with(
        query="question", project_id=PROJECT_ID, top_k=settings.top_k
    )


def test_query_raises_when_project_is_missing() -> None:
    # Arrange
    session = MagicMock()
    query_engine = MagicMock()
    session.get.return_value = None
    service = QueryService(session, query_engine)

    # Act / Assert
    with pytest.raises(ProjectNotFoundError):
        service.query("question", project_id=PROJECT_ID)

    query_engine.query.assert_not_called()


def test_query_rejects_streaming_response() -> None:
    # Arrange
    session = MagicMock()
    query_engine = MagicMock()
    session.get.return_value = Project(id=PROJECT_ID, name="Research")
    query_engine.query.return_value = "streaming response"
    service = QueryService(session, query_engine)

    # Act / Assert
    with pytest.raises(TypeError, match="Streaming responses are not supported"):
        service.query("question", project_id=PROJECT_ID)
