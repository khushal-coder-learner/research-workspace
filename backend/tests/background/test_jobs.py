import logging
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.background import jobs
from app.background.schemas import IngestionJob
from app.ingestion.service import IngestionService


@pytest.fixture
def job() -> IngestionJob:
    return IngestionJob(
        document_id=UUID("11111111-1111-1111-1111-111111111111"),
        project_id=UUID("22222222-2222-2222-2222-222222222222"),
    )


@pytest.fixture
def ingestion_service() -> MagicMock:
    return MagicMock(spec=IngestionService)


def test_process_ingestion_job_ingests_document(
    job: IngestionJob, ingestion_service: MagicMock
) -> None:
    # Arrange

    # Act
    result = jobs.process_ingestion_job(job, ingestion_service)

    # Assert
    assert result is None
    ingestion_service.ingest_document.assert_called_once_with(job.document_id)


def test_process_ingestion_job_logs_start_and_successful_completion(
    job: IngestionJob,
    ingestion_service: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    caplog.set_level(logging.INFO, logger=jobs.logger.name)

    # Act
    jobs.process_ingestion_job(job, ingestion_service)

    # Assert
    messages = [record.getMessage() for record in caplog.records]
    assert messages == [
        "Starting document ingestion",
        "Completed document ingestion",
    ]


def test_process_ingestion_job_propagates_service_failure_without_success_log(
    job: IngestionJob,
    ingestion_service: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    caplog.set_level(logging.INFO, logger=jobs.logger.name)
    ingestion_service.ingest_document.side_effect = RuntimeError("ingestion failed")

    # Act / Assert
    with pytest.raises(RuntimeError, match="ingestion failed"):
        jobs.process_ingestion_job(job, ingestion_service)

    ingestion_service.ingest_document.assert_called_once_with(job.document_id)
    messages = [record.getMessage() for record in caplog.records]
    assert messages == ["Starting document ingestion"]
