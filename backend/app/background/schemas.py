from uuid import UUID

from pydantic import BaseModel


class IngestionJob(BaseModel):
    """Message placed on the document ingestion queue."""

    document_id: UUID
    project_id: UUID
    retry_count: int = 0
