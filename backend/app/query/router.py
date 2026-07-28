from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import get_query_service
from app.query.schemas import QueryRequest, QueryResponse
from app.query.service import QueryService

router = APIRouter(tags=["query"])


@router.post(
    "/projects/{project_id}/query",
)
def query_project(
    project_id: UUID,
    request: QueryRequest,
    query_service: QueryService = Depends(get_query_service),
) -> QueryResponse :
    response = query_service.query(
        query=request.query,
        project_id=project_id,
    )

    return response