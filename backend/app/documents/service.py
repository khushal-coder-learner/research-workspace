from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.documents.models import Document, DocumentStatus
from app.projects.models import Project


class ProjectNotFoundError(Exception):
    pass


class DocumentNotFoundError(Exception):
    pass


class InvalidDocumentUploadError(Exception):
    pass


DOCUMENT_STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "documents"


def _get_project(session: Session, project_id: UUID) -> Project:
    statement = select(Project).where(Project.id == project_id)
    project = session.scalar(statement)

    if project is None:
        raise ProjectNotFoundError

    return project


def _validate_pdf_upload(filename: str | None, content_type: str | None) -> None:
    if not filename:
        raise InvalidDocumentUploadError

    if Path(filename).suffix.lower() != ".pdf":
        raise InvalidDocumentUploadError

    allowed_content_types = {"application/pdf", "application/x-pdf"}
    if content_type not in allowed_content_types:
        raise InvalidDocumentUploadError


def upload_document(
    session: Session,
    project_id: UUID,
    filename: str | None,
    content_type: str | None,
    file_bytes: bytes,
) -> Document:
    _get_project(session, project_id)
    _validate_pdf_upload(filename, content_type)
    if filename is None:
        raise InvalidDocumentUploadError

    DOCUMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4()}.pdf"
    file_path = DOCUMENT_STORAGE_DIR / stored_filename

    file_path.write_bytes(file_bytes)

    document = Document(
        project_id=project_id,
        filename=filename,
        file_path=str(file_path),
        status=DocumentStatus.UPLOADED,
    )

    try:
        session.add(document)
        session.commit()
        session.refresh(document)
    except Exception:
        session.rollback()
        if file_path.exists():
            file_path.unlink()
        raise

    return document


def list_documents(session: Session, project_id: UUID) -> list[Document]:
    _get_project(session, project_id)

    statement = (
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.created_at.desc())
    )
    return list(session.scalars(statement).all())


def get_document(session: Session, document_id: UUID) -> Document:
    statement = select(Document).where(Document.id == document_id)
    document = session.scalar(statement)

    if document is None:
        raise DocumentNotFoundError

    return document
