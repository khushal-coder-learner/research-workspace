from sqlalchemy.orm import Session

from llama_index.readers.file import PyMuPDFReader
from app.ingestion.document_ingestion import DocumentIngestion
from app.ingestion.service import IngestionService
from app.ingestion.persistence import storage_context
from app.ingestion.transformations import TRANSFORMATIONS
from app.providers.embedding import embedding_model

def build_document_ingestor() -> DocumentIngestion:
    """Return a configured document ingestor."""

    reader = PyMuPDFReader()

    return DocumentIngestion(
        reader=reader,
        transformations=TRANSFORMATIONS,
        storage_context=storage_context,
        embed_model=embedding_model,
    )

def build_ingestion_service(
    session: Session,
) -> IngestionService:
    return IngestionService(
        session=session,
        ingestor=build_document_ingestor(),
    )