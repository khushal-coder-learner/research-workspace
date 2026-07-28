from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.documents.models import Document
from app.documents.models import DocumentStatus
from app.ingestion.document_ingestion import DocumentIngestion


class IngestionService:
    """Application service responsible for ingesting documents."""

    def __init__(
        self,
        session: Session,
        ingestor: DocumentIngestion,
    ) -> None:
        self._session = session
        self._ingestor = ingestor

    def ingest_document(self, document_id: UUID) -> Document:
        document = self._session.get(Document, document_id)

        if document is None:
            raise ValueError(f"Document '{document_id}' not found.")

        if document.status == DocumentStatus.INDEXED:
            return document

        document.status = DocumentStatus.PROCESSING
        self._session.commit()

        try:
            self._ingestor.ingest(
                pdf_path=Path(document.file_path),
                project_id=document.project_id,
                document_id=document.id,
                filename=document.filename,
            )

            document.status = DocumentStatus.INDEXED

        except Exception:
            document.status = DocumentStatus.FAILED
            self._session.commit()
            raise

        self._session.commit()

        return document