from __future__ import annotations

import logging

from app.background.schemas import IngestionJob
from app.ingestion.service import IngestionService

logger = logging.getLogger(__name__)


def process_ingestion_job(job: IngestionJob, service: IngestionService) -> None:
    """Execute one queued ingestion using the existing application service."""

    logger.info("Starting document ingestion", extra={"document_id": str(job.document_id), "project_id": str(job.project_id)})
    service.ingest_document(job.document_id)
    logger.info("Completed document ingestion", extra={"document_id": str(job.document_id), "project_id": str(job.project_id)})
