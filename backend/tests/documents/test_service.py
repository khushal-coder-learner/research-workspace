from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.core.exceptions import QueueUnavailableError
from app.background.queue import QueueError
from app.documents.models import DocumentStatus
from app.documents.service import upload_document
from app.projects.models import Project


PROJECT_ID = UUID("22222222-2222-2222-2222-222222222222")
DOCUMENT_ID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def queue() -> MagicMock:
    return MagicMock()


def configure_refresh(session: MagicMock) -> None:
    def refresh(document: object) -> None:
        document.id = DOCUMENT_ID

    session.refresh.side_effect = refresh


def test_upload_document_stores_commits_queues_and_marks_document_queued(
    session: MagicMock, queue: MagicMock, tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    from app.documents import service

    monkeypatch.setattr(service, "DOCUMENT_STORAGE_DIR", tmp_path)
    session.scalar.return_value = Project(id=PROJECT_ID, name="Research")
    configure_refresh(session)

    # Act
    document = upload_document(
        session,
        PROJECT_ID,
        "paper.pdf",
        "application/pdf",
        b"pdf bytes",
        queue,
    )

    # Assert
    assert document.status == DocumentStatus.QUEUED
    assert document.filename == "paper.pdf"
    assert list(tmp_path.iterdir())
    queue.enqueue.assert_called_once()
    queued_job = queue.enqueue.call_args.args[0]
    assert queued_job.document_id == DOCUMENT_ID
    assert queued_job.project_id == PROJECT_ID
    assert session.commit.call_count == 2
    session.refresh.assert_called_once_with(document)


@pytest.mark.parametrize(
    ("filename", "content_type"),
    [
        (None, "application/pdf"),
        ("paper.txt", "application/pdf"),
        ("paper.pdf", "text/plain"),
    ],
)
def test_upload_document_rejects_invalid_pdf_upload(
    session: MagicMock,
    queue: MagicMock,
    filename: str | None,
    content_type: str,
) -> None:
    # Arrange
    session.scalar.return_value = Project(id=PROJECT_ID, name="Research")

    # Act / Assert
    from app.core.exceptions import InvalidDocumentUploadError

    with pytest.raises(InvalidDocumentUploadError):
        upload_document(
            session, PROJECT_ID, filename, content_type, b"data", queue
        )

    session.add.assert_not_called()
    queue.enqueue.assert_not_called()


def test_upload_document_rejects_missing_project(
    session: MagicMock, queue: MagicMock
) -> None:
    # Arrange
    session.scalar.return_value = None

    # Act / Assert
    from app.core.exceptions import ProjectNotFoundError

    with pytest.raises(ProjectNotFoundError):
        upload_document(
            session, PROJECT_ID, "paper.pdf", "application/pdf", b"data", queue
        )

    session.add.assert_not_called()


def test_upload_document_rolls_back_and_removes_file_when_database_commit_fails(
    session: MagicMock,
    queue: MagicMock,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    from app.documents import service

    monkeypatch.setattr(service, "DOCUMENT_STORAGE_DIR", tmp_path)
    session.scalar.return_value = Project(id=PROJECT_ID, name="Research")
    session.commit.side_effect = RuntimeError("database unavailable")

    # Act / Assert
    with pytest.raises(RuntimeError, match="database unavailable"):
        upload_document(
            session, PROJECT_ID, "paper.pdf", "application/pdf", b"data", queue
        )

    session.rollback.assert_called_once_with()
    assert list(tmp_path.iterdir()) == []
    queue.enqueue.assert_not_called()


def test_upload_document_marks_queue_failure_and_rolls_back(
    session: MagicMock,
    queue: MagicMock,
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    from app.documents import service

    monkeypatch.setattr(service, "DOCUMENT_STORAGE_DIR", tmp_path)
    session.scalar.return_value = Project(id=PROJECT_ID, name="Research")
    configure_refresh(session)
    session.commit.side_effect = [None, None]
    queue.enqueue.side_effect = QueueError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueUnavailableError):
        upload_document(
            session, PROJECT_ID, "paper.pdf", "application/pdf", b"data", queue
        )

    assert session.add.call_count == 1
    session.rollback.assert_called_once_with()
    assert session.commit.call_count == 2
