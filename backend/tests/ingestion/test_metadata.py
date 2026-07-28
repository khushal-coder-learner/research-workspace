from types import SimpleNamespace
from uuid import UUID

from app.ingestion.metadata import enrich_documents


PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")
DOCUMENT_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_enrich_documents_adds_retrieval_metadata_and_removes_file_metadata() -> None:
    # Arrange
    document = SimpleNamespace(
        metadata={"source": "4", "file_path": "/tmp/paper.pdf", "author": "Ada"}
    )

    # Act
    result = enrich_documents(
        [document],
        project_id=PROJECT_ID,
        document_id=DOCUMENT_ID,
        filename="paper.pdf",
    )

    # Assert
    assert result == [document]
    assert document.metadata == {
        "project_id": str(PROJECT_ID),
        "document_id": str(DOCUMENT_ID),
        "filename": "paper.pdf",
        "page_number": 4,
        "author": "Ada",
    }


def test_enrich_documents_defaults_missing_source_to_page_zero() -> None:
    # Arrange
    document = SimpleNamespace(metadata={})

    # Act
    enrich_documents(
        [document],
        project_id=PROJECT_ID,
        document_id=DOCUMENT_ID,
        filename="paper.pdf",
    )

    # Assert
    assert document.metadata["page_number"] == 0


def test_enrich_documents_handles_multiple_documents() -> None:
    # Arrange
    documents = [
        SimpleNamespace(metadata={"source": 1}),
        SimpleNamespace(metadata={"source": 2}),
    ]

    # Act
    result = enrich_documents(
        documents,
        project_id=PROJECT_ID,
        document_id=DOCUMENT_ID,
        filename="paper.pdf",
    )

    # Assert
    assert result == documents
    assert [document.metadata["page_number"] for document in documents] == [1, 2]
