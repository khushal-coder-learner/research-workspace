from uuid import UUID

from sqlalchemy.orm import Session

from llama_index.core.base.response.schema import Response

from app.core.config import settings
from app.projects.models import Project
from app.core.exceptions import ProjectNotFoundError
from app.query.query_engine import QueryEngine
from app.query.mapper import to_query_response


class QueryService:
    def __init__(
        self,
        session: Session,
        query_engine: QueryEngine,
    ) -> None:
        self._session = session
        self._query_engine = query_engine

    def query(
        self,
        query: str,
        *,
        project_id: UUID,
    ):
        project = self._session.get(Project, project_id)

        if project is None:
            raise ProjectNotFoundError

        response = self._query_engine.query(
            query=query,
            project_id=project_id,
            top_k=settings.top_k,
        )
        if not isinstance(response, Response):
            raise TypeError("Streaming responses are not supported.")

        return to_query_response(response)
        