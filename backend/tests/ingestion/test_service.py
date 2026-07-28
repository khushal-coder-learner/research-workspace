from pathlib import Path
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.documents.models import Document, DocumentStatus
from app.ingestion.service import IngestionService


DOCUMENT_ID = UUID("11111111-1111-1111-1111-111111111111")
PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def ingestor() -> MagicMock:
    return MagicMock()


def make_document(status: DocumentStatus = DocumentStatus.UPLOADED) -> Document:
    return Document(
        id=DOCUMENT_ID,
        project_id=PROJECT_ID,
        filename="paper.pdf",
        file_path="storage/paper.pdf",
        status=status,
    )


def test_ingest_document_marks_document_indexed_after_success(
    session: MagicMock, ingestor: MagicMock
) -> None:
    # Arrange
    document = make_document()
    session.get.return_value = document
    service = IngestionService(session, ingestor)

    # Act
    result = service.ingest_document(DOCUMENT_ID)

    # Assert
    assert result is document
    assert document.status == DocumentStatus.INDEXED
    assert session.commit.call_count == 2
    ingestor.ingest.assert_called_once_with(
        pdf_path=Path(document.file_path),
        project_id=PROJECT_ID,
        document_id=DOCUMENT_ID,
        filename="paper.pdf",
    )


def test_ingest_document_returns_indexed_document_without_reprocessing(
    session: MagicMock, ingestor: MagicMock
) -> None:
    # Arrange
    document = make_document(DocumentStatus.INDEXED)
    session.get.return_value = document
    service = IngestionService(session, ingestor)

    # Act
    result = service.ingest_document(DOCUMENT_ID)

    # Assert
    assert result is document
    ingestor.ingest.assert_not_called()
    session.commit.assert_not_called()


def test_ingest_document_raises_when_document_is_missing(
    session: MagicMock, ingestor: MagicMock
) -> None:
    # Arrange
    session.get.return_value = None
    service = IngestionService(session, ingestor)

    # Act / Assert
    with pytest.raises(ValueError, match=str(DOCUMENT_ID)):
        service.ingest_document(DOCUMENT_ID)

    ingestor.ingest.assert_not_called()


def test_ingest_document_marks_failed_and_commits_when_ingestion_fails(
    session: MagicMock, ingestor: MagicMock
) -> None:
    # Arrange
    document = make_document()
    session.get.return_value = document
    ingestor.ingest.side_effect = RuntimeError("parser failed")
    service = IngestionService(session, ingestor)

    # Act / Assert
    with pytest.raises(RuntimeError, match="parser failed"):
        service.ingest_document(DOCUMENT_ID)

    assert document.status == DocumentStatus.FAILED
    assert session.commit.call_count == 2
