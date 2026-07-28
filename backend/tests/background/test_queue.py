from unittest.mock import MagicMock
from uuid import UUID

import pytest
from redis import Redis
from redis.exceptions import RedisError

from app.background.queue import QueueError, RedisBackgroundQueue
from app.background.schemas import IngestionJob


@pytest.fixture
def redis_client() -> MagicMock:
    return MagicMock(spec=Redis)


@pytest.fixture
def queue(redis_client: MagicMock) -> RedisBackgroundQueue:
    return RedisBackgroundQueue(redis_client, max_retries=3)


@pytest.fixture
def job() -> IngestionJob:
    return IngestionJob(
        document_id=UUID("11111111-1111-1111-1111-111111111111"),
        project_id=UUID("22222222-2222-2222-2222-222222222222"),
    )


def test_enqueue_publishes_job_to_pending_queue(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange

    # Act
    result = queue.enqueue(job)

    # Assert
    assert result is None
    redis_client.rpush.assert_called_once_with(queue._pending_key, job.model_dump_json())


def test_enqueue_raises_queue_error_when_redis_fails(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.rpush.side_effect = RedisError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to enqueue"):
        queue.enqueue(job)


def test_reserve_returns_valid_job_from_processing_queue(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.blmove.return_value = job.model_dump_json()

    # Act
    result = queue.reserve(timeout=5)

    # Assert
    assert result == job
    redis_client.blmove.assert_called_once_with(
        queue._pending_key,
        queue._processing_key,
        timeout=5,
        src="LEFT",
        dest="RIGHT",
    )


def test_reserve_returns_none_when_pending_queue_is_empty(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    redis_client.blmove.return_value = None

    # Act
    result = queue.reserve()

    # Assert
    assert result is None


def test_reserve_raises_queue_error_for_invalid_payload(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    invalid_payload = "not valid json"
    redis_client.blmove.return_value = invalid_payload

    # Act / Assert
    with pytest.raises(QueueError, match="invalid job"):
        queue.reserve()

    # The payload has already been moved to processing by Redis.
    redis_client.blmove.assert_called_once_with(
        queue._pending_key,
        queue._processing_key,
        timeout=0,
        src="LEFT",
        dest="RIGHT",
    )


def test_reserve_raises_queue_error_when_redis_fails(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    redis_client.blmove.side_effect = RedisError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to reserve"):
        queue.reserve()


def test_ack_removes_job_from_processing_queue(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.return_value = 1

    # Act
    result = queue.ack(job)

    # Assert
    assert result is None
    redis_client.lrem.assert_called_once_with(
        queue._processing_key, 1, job.model_dump_json()
    )


def test_ack_raises_queue_error_when_job_is_not_found(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.return_value = 0

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to acknowledge"):
        queue.ack(job)


def test_ack_raises_queue_error_when_redis_fails(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.side_effect = RedisError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to acknowledge"):
        queue.ack(job)


def test_retry_increments_count_and_requeues_job_to_pending(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.return_value = 1

    # Act
    result = queue.retry(job)

    # Assert
    assert result is True
    updated_job = job.model_copy(update={"retry_count": 1})
    redis_client.lrem.assert_called_once_with(
        queue._processing_key, 1, job.model_dump_json()
    )
    redis_client.rpush.assert_called_once_with(
        queue._pending_key, updated_job.model_dump_json()
    )


def test_retry_keeps_job_pending_at_max_retries(
    redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    queue = RedisBackgroundQueue(redis_client, max_retries=3)
    job = job.model_copy(update={"retry_count": 2})
    redis_client.lrem.return_value = 1

    # Act
    result = queue.retry(job)

    # Assert
    assert result is True
    updated_job = job.model_copy(update={"retry_count": 3})
    redis_client.rpush.assert_called_once_with(
        queue._pending_key, updated_job.model_dump_json()
    )


def test_retry_moves_job_to_dead_letter_after_max_retries(
    redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    queue = RedisBackgroundQueue(redis_client, max_retries=3)
    job = job.model_copy(update={"retry_count": 3})
    redis_client.lrem.return_value = 1

    # Act
    result = queue.retry(job)

    # Assert
    assert result is False
    updated_job = job.model_copy(update={"retry_count": 4})
    redis_client.lrem.assert_called_once_with(
        queue._processing_key, 1, job.model_dump_json()
    )
    redis_client.rpush.assert_called_once_with(
        queue._dead_letter_key, updated_job.model_dump_json()
    )


def test_retry_raises_queue_error_when_job_is_missing_from_processing(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.return_value = 0

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to locate reserved job"):
        queue.retry(job)

    redis_client.rpush.assert_not_called()


def test_retry_raises_queue_error_when_redis_fails(
    queue: RedisBackgroundQueue, redis_client: MagicMock, job: IngestionJob
) -> None:
    # Arrange
    redis_client.lrem.side_effect = RedisError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to retry"):
        queue.retry(job)


def test_recover_returns_zero_when_processing_queue_is_empty(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    redis_client.rpoplpush.return_value = None

    # Act
    result = queue.recover()

    # Assert
    assert result == 0
    redis_client.rpoplpush.assert_called_once_with(queue._processing_key, queue._pending_key)


def test_recover_moves_all_processing_jobs_to_pending_and_counts_them(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    redis_client.rpoplpush.side_effect = ["job-one", "job-two", None]

    # Act
    result = queue.recover()

    # Assert
    assert result == 2
    assert redis_client.rpoplpush.call_count == 3
    redis_client.rpoplpush.assert_any_call(queue._processing_key, queue._pending_key)


def test_recover_raises_queue_error_when_redis_fails(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange
    redis_client.rpoplpush.side_effect = RedisError("Redis unavailable")

    # Act / Assert
    with pytest.raises(QueueError, match="Unable to recover"):
        queue.recover()


def test_close_closes_redis_client(
    queue: RedisBackgroundQueue, redis_client: MagicMock
) -> None:
    # Arrange

    # Act
    result = queue.close()

    # Assert
    assert result is None
    redis_client.close.assert_called_once_with()
