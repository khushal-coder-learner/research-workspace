from __future__ import annotations

import logging
import app.models

from app.background.jobs import process_ingestion_job
from app.background.queue import QueueError, RedisBackgroundQueue
from app.core.composition import build_ingestion_service
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.redis.client import redis_client

logger = logging.getLogger(__name__)


def run_worker() -> None:
    """Consume ingestion jobs until the worker receives an interrupt."""

    queue = RedisBackgroundQueue(redis_client)

    try:
        recovered = queue.recover()
        if recovered > 0:
            logger.warning(
                "Recovered abandoned ingestion jobs",
                extra={"count": recovered},
            )

    except QueueError:
        logger.exception("Unable to recover ingestion jobs")

    logger.info("Document ingestion worker started")

    try:
        while True:
            try:
                job = queue.reserve()
            except QueueError:
                logger.exception("Unable to consume document ingestion queue")
                continue

            if job is None:
                continue

            session = SessionLocal()
            try:
                process_ingestion_job(
                    job,
                    build_ingestion_service(session=session),
                )

            except Exception:
                logger.exception(
                    "Document ingestion failed",
                    extra={"document_id": str(job.document_id)},
                )

                try:
                    requeued = queue.retry(job)

                    if requeued:
                        logger.info(
                            "Document ingestion job scheduled for retry",
                            extra={
                                "document_id": str(job.document_id),
                                "project_id": str(job.project_id),
                                "retry_count": job.retry_count + 1,
                            },
                        )
                    else:
                        logger.error(
                            "Document ingestion job moved to dead letter queue",
                            extra={
                                "document_id": str(job.document_id),
                                "project_id": str(job.project_id),
                                "retry_count": job.retry_count + 1,
                            },
                        )
                        
                except QueueError:
                    logger.exception(
                        "Unable to retry ingestion job",
                        extra={
                            "document_id": str(job.document_id),
                        },
                    )

            else:
                try:
                    queue.ack(job)
                    logger.info(
                        "Acknowledged ingestion job",
                        extra={
                            "document_id": str(job.document_id),
                            "project_id": str(job.project_id),
                        },
                    )

                except QueueError:
                    logger.exception(
                        "Unable to acknowledge ingestion job",
                        extra={"document_id": str(job.document_id)},
                    )

            finally:
                session.close()
    except KeyboardInterrupt:
        logger.info("Document ingestion worker stopping")
    finally:
        queue.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_worker()
