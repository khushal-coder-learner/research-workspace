from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.dependencies import DBSession
from app.documents.schemas import DocumentRead
from app.documents.service import (
    DocumentNotFoundError,
    InvalidDocumentUploadError,
    ProjectNotFoundError,
    get_document,
    list_documents,
    upload_document,
)

from app.documents.models import Document

router = APIRouter(tags=["documents"])


def _map_document_error(exception: Exception) -> HTTPException:
    if isinstance(exception, ProjectNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if isinstance(exception, DocumentNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Only PDF uploads are allowed",
    )


@router.post("/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document_route(
    db: DBSession,
    project_id: UUID = Form(...),
    uploaded_file: UploadFile = File(...),
) -> Document:
    file_bytes = await uploaded_file.read()

    try:
        document = upload_document(
            session=db,
            project_id=project_id,
            filename=uploaded_file.filename,
            content_type=uploaded_file.content_type,
            file_bytes=file_bytes,
        )
    except (ProjectNotFoundError, InvalidDocumentUploadError) as exception:
        raise _map_document_error(exception) from exception

    return document


@router.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_documents_route(
    project_id: UUID,
    db: DBSession,
) -> list[Document]:
    try:
        documents = list_documents(db, project_id)
    except ProjectNotFoundError as exception:
        raise _map_document_error(exception) from exception

    return [document for document in documents]


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_route(
    document_id: UUID,
    db: DBSession,
) -> Document:
    try:
        document = get_document(db, document_id)
    except DocumentNotFoundError as exception:
        raise _map_document_error(exception) from exception

    return document
