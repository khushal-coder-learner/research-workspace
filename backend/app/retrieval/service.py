from uuid import UUID

from sqlalchemy.orm import Session

from app.projects.models import Project
from app.retrieval.retriever import ProjectRetriever
from app.core.exceptions import ProjectNotFoundError


class RetrievalService:
    def __init__(
        self,
        session: Session,
        retriever: ProjectRetriever,
    ) -> None:
        self._session = session
        self._retriever = retriever

    def retrieve(
        self,
        query: str,
        *,
        project_id: UUID,
        top_k: int,
    ):
        project = self._session.get(Project, project_id)

        if project is None:
            raise ProjectNotFoundError

        return self._retriever.retrieve(
            query=query,
            project_id=project_id,
            top_k=top_k,
        )