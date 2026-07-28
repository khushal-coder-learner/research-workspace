from __future__ import annotations

from uuid import UUID

from fastapi import Depends, APIRouter, File, Form, UploadFile, status

from app.background.queue import BackgroundQueue
from app.core.dependencies import DBSession, get_ingestion_queue
from app.core.exceptions import (ProjectNotFoundError, DocumentNotFoundError, InvalidDocumentUploadError)
from app.documents.schemas import DocumentRead
from app.documents.service import (
    get_document,
    list_documents,
    upload_document,
)

from app.documents.models import Document

router = APIRouter(tags=["documents"])

@router.post("/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document_route(
    db: DBSession,
    ingestion_queue: BackgroundQueue = Depends(get_ingestion_queue),
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
            ingestion_queue=ingestion_queue
        )
    except (ProjectNotFoundError, InvalidDocumentUploadError) as exception:
        raise exception from exception

    return document


@router.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_documents_route(
    project_id: UUID,
    db: DBSession,
) -> list[Document]:
    try:
        documents = list_documents(db, project_id)
    except ProjectNotFoundError as exception:
        raise exception from exception

    return [document for document in documents]


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_route(
    document_id: UUID,
    db: DBSession,
) -> Document:
    try:
        document = get_document(db, document_id)
    except DocumentNotFoundError as exception:
        raise exception from exception

    return document
