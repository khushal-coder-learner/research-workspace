from __future__ import annotations

from typing import Protocol

from redis import Redis
from redis.exceptions import RedisError

from app.background.schemas import IngestionJob


class QueueError(RuntimeError):
    """Raised when a job cannot be published or consumed."""


class BackgroundQueue(Protocol):

    def enqueue(self, job: IngestionJob) -> None:
        ...

    def reserve(self) -> IngestionJob | None:
        ...

    def ack(self, job: IngestionJob) -> None:
        ...

    def retry(self, job: IngestionJob) -> None:
        ...

    def recover(self) -> int: 
        ...

    def close(self) -> None:
        ...


class RedisBackgroundQueue:
    """Redis-backed implementation of the ingestion queue port."""
    PENDING_SUFFIX = ":pending"
    PROCESSING_SUFFIX = ":processing"
    DEAD_LETTER_SUFFIX = ":dead-letter"

    def __init__(self, client: Redis, *, key: str = "document-ingestion", max_retries: int = 3) -> None:
        self._client = client
        self._pending_key = f"{key}{self.PENDING_SUFFIX}"
        self._processing_key = f"{key}{self.PROCESSING_SUFFIX}"
        self._dead_letter_key = f"{key}{self.DEAD_LETTER_SUFFIX}"
        self._max_retries = max_retries

    def enqueue(self, job: IngestionJob) -> None:
        try:
            self._client.rpush(self._pending_key, job.model_dump_json())
        except RedisError as exception:
            raise QueueError("Unable to enqueue document ingestion job.") from exception

    def reserve(self, timeout: int = 0) -> IngestionJob | None:
        try:
            payload = self._client.blmove(
                self._pending_key,
                self._processing_key,
                timeout=timeout,
                src="LEFT",
                dest="RIGHT",
            )
        except RedisError as exception:
            raise QueueError(
                "Unable to reserve document ingestion job."
            ) from exception

        if payload is None:
            return None

        try:
            return IngestionJob.model_validate_json(payload)
        except ValueError as exception:
            raise QueueError(
                "The ingestion queue contained an invalid job."
            ) from exception

    def ack(self, job: IngestionJob) -> None:
        try:
            removed = self._client.lrem(
                self._processing_key,
                1,
                job.model_dump_json(),
            )

            if removed != 1:
                raise QueueError(
                    "Unable to acknowledge ingestion job."
                )

        except RedisError as exception:
            raise QueueError(
                "Unable to acknowledge ingestion job."
            ) from exception

    def retry(self, job: IngestionJob) -> bool:
        original_payload = job.model_dump_json()

        retry_job = job.model_copy(
            update={
                "retry_count": job.retry_count + 1,
            }
        )

        retry_payload = retry_job.model_dump_json()

        destination = (
            self._pending_key
            if retry_job.retry_count <= self._max_retries
            else self._dead_letter_key
        )

        try:
            removed = self._client.lrem(
                self._processing_key,
                1,
                original_payload,
            )

            if removed != 1:
                raise QueueError(
                    "Unable to locate reserved job."
                )

            self._client.rpush(
                destination,
                retry_payload,
            )

            return True if destination == self._pending_key else False

        except RedisError as exc:
            raise QueueError(
                "Unable to retry job."
            ) from exc

    def recover(self) -> int:
        recovered = 0

        try:
            while True:
                payload = self._client.rpoplpush(
                    self._processing_key,
                    self._pending_key,
                )

                if payload is None:
                    break

                recovered += 1

            return recovered

        except RedisError as exc:
            raise QueueError(
                "Unable to recover ingestion jobs."
            ) from exc

    def close(self) -> None:
        self._client.close()
