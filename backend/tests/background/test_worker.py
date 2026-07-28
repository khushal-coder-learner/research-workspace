from dataclasses import dataclass
import logging
from unittest.mock import MagicMock, call
from uuid import UUID

import pytest

from app.background import worker
from app.background.queue import QueueError
from app.background.schemas import IngestionJob

@dataclass
class WorkerMocks:
    queue: MagicMock
    session: MagicMock
    ingestion_service: MagicMock
    queue_factory: MagicMock
    session_factory: MagicMock
    service_factory: MagicMock
    process_job: MagicMock

@pytest.fixture
def job() -> IngestionJob:
    return IngestionJob(
        document_id=UUID("11111111-1111-1111-1111-111111111111"),
        project_id=UUID("22222222-2222-2222-2222-222222222222"),
    )


@pytest.fixture
def worker_mocks(monkeypatch: pytest.MonkeyPatch) -> WorkerMocks:
    queue = MagicMock(name="queue")
    queue.recover.return_value = 0
    session = MagicMock(name="session")
    ingestion_service = MagicMock(name="ingestion_service")
    queue_factory = MagicMock(name="queue_factory", return_value=queue)
    session_factory = MagicMock(name="session_factory", return_value=session)
    service_factory = MagicMock(
        name="service_factory", return_value=ingestion_service
    )
    process_job = MagicMock(name="process_job")

    monkeypatch.setattr(worker, "RedisBackgroundQueue", queue_factory)
    monkeypatch.setattr(worker, "SessionLocal", session_factory)
    monkeypatch.setattr(worker, "build_ingestion_service", service_factory)
    monkeypatch.setattr(worker, "process_ingestion_job", process_job)

    return WorkerMocks(
        queue=queue,
        session=session,
        ingestion_service=ingestion_service,
        queue_factory=queue_factory,
        session_factory=session_factory,
        service_factory=service_factory,
        process_job=process_job,
    )


def test_worker_recovers_jobs_once_before_processing(
    worker_mocks: WorkerMocks,
    job: IngestionJob,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    caplog.set_level(logging.INFO, logger=worker.logger.name)
    queue = worker_mocks.queue
    process_job = worker_mocks.process_job
    queue.recover.return_value = 2
    queue.reserve.side_effect = [job, KeyboardInterrupt]

    # Act
    worker.run_worker()

    # Assert
    queue.recover.assert_called_once_with()
    assert queue.method_calls[:2] == [call.recover(), call.reserve()]
    process_job.assert_called_once_with(
        job, worker_mocks.ingestion_service
    )
    assert "Recovered abandoned ingestion jobs" in caplog.text


def test_worker_logs_recovery_failure_and_continues(
    worker_mocks: WorkerMocks , job: IngestionJob, caplog: pytest.LogCaptureFixture
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.recover.side_effect = QueueError("recovery failed")
    queue.reserve.side_effect = [job, KeyboardInterrupt]

    # Act
    worker.run_worker()

    # Assert
    queue.recover.assert_called_once_with()
    worker_mocks.process_job.assert_called_once()
    assert "Unable to recover ingestion jobs" in caplog.text


def test_worker_processes_job_and_acknowledges_successfully(
    worker_mocks: WorkerMocks, job: IngestionJob
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.recover.return_value = 0
    queue.reserve.side_effect = [job, KeyboardInterrupt]

    # Act
    worker.run_worker()

    # Assert
    worker_mocks.process_job.assert_called_once_with(
        job, worker_mocks.ingestion_service
    )
    worker_mocks.service_factory.assert_called_once_with(
        session=worker_mocks.session_factory()
    )
    queue.ack.assert_called_once_with(job)
    queue.retry.assert_not_called()
    worker_mocks.session.close.assert_called_once_with()


def test_worker_retries_job_when_processing_fails(
    worker_mocks: WorkerMocks, job: IngestionJob
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.recover.return_value = 0
    queue.reserve.side_effect = [job, KeyboardInterrupt]
    worker_mocks.process_job.side_effect = RuntimeError("ingestion failed")
    queue.retry.return_value = True

    # Act
    worker.run_worker()

    # Assert
    worker_mocks.process_job.assert_called_once()
    queue.retry.assert_called_once_with(job)
    queue.ack.assert_not_called()
    worker_mocks.session.close.assert_called_once_with()


def test_worker_closes_session_when_ingestion_service_build_fails(
    worker_mocks: WorkerMocks, job: IngestionJob
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = [job, KeyboardInterrupt]
    worker_mocks.service_factory.side_effect = RuntimeError(
        "service construction failed"
    )
    queue.retry.return_value = True

    # Act
    worker.run_worker()

    # Assert
    worker_mocks.service_factory.assert_called_once_with(
        session=worker_mocks.session_factory()
    )
    queue.retry.assert_called_once_with(job)
    queue.ack.assert_not_called()
    worker_mocks.session.close.assert_called_once_with()


@pytest.mark.parametrize(
    ("retry_result", "expected_log"),
    [
        (True, "scheduled for retry"),
        (False, "moved to dead letter queue"),
    ],
)
def test_worker_logs_retry_result_for_requeued_or_dead_letter_job(
    worker_mocks: WorkerMocks,
    job: IngestionJob,
    retry_result: bool,
    expected_log: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Arrange
    caplog.set_level(logging.INFO, logger=worker.logger.name)
    queue = worker_mocks.queue
    queue.reserve.side_effect = [job, KeyboardInterrupt]
    worker_mocks.process_job.side_effect = RuntimeError("ingestion failed")
    queue.retry.return_value = retry_result

    # Act
    worker.run_worker()

    # Assert
    queue.retry.assert_called_once_with(job)
    assert expected_log in caplog.text


def test_worker_continues_after_reserve_queue_error(
    worker_mocks: WorkerMocks, caplog: pytest.LogCaptureFixture
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = [QueueError("reserve failed"), KeyboardInterrupt]

    # Act
    worker.run_worker()

    # Assert
    assert queue.reserve.call_count == 2
    worker_mocks.session_factory.assert_not_called()
    assert "Unable to consume document ingestion queue" in caplog.text


def test_worker_logs_retry_queue_error_and_closes_session(
    worker_mocks: WorkerMocks, job: IngestionJob, caplog: pytest.LogCaptureFixture
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = [job, KeyboardInterrupt]
    worker_mocks.process_job.side_effect = RuntimeError("ingestion failed")
    queue.retry.side_effect = QueueError("retry failed")

    # Act
    worker.run_worker()

    # Assert
    queue.retry.assert_called_once_with(job)
    queue.ack.assert_not_called()
    worker_mocks.session.close.assert_called_once_with()
    assert "Unable to retry ingestion job" in caplog.text


def test_worker_logs_ack_queue_error_and_does_not_retry(
    worker_mocks: WorkerMocks, job: IngestionJob, caplog: pytest.LogCaptureFixture
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = [job, KeyboardInterrupt]
    queue.ack.side_effect = QueueError("ack failed")

    # Act
    worker.run_worker()

    # Assert
    queue.ack.assert_called_once_with(job)
    queue.retry.assert_not_called()
    worker_mocks.session.close.assert_called_once_with()
    assert "Unable to acknowledge ingestion job" in caplog.text


def test_worker_skips_empty_reservation_without_creating_session(
    worker_mocks: WorkerMocks
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = [None, KeyboardInterrupt]

    # Act
    worker.run_worker()

    # Assert
    worker_mocks.session_factory.assert_not_called()
    worker_mocks.process_job.assert_not_called()
    queue.ack.assert_not_called()
    queue.retry.assert_not_called()


def test_worker_exits_cleanly_on_keyboard_interrupt(
    worker_mocks: WorkerMocks
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = KeyboardInterrupt

    # Act
    worker.run_worker()

    # Assert
    queue.reserve.assert_called_once_with()


def test_worker_closes_queue_on_shutdown(
    worker_mocks: WorkerMocks
) -> None:
    # Arrange
    queue = worker_mocks.queue
    queue.reserve.side_effect = KeyboardInterrupt

    # Act
    worker.run_worker()

    # Assert
    queue.close.assert_called_once_with()
