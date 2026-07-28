from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal
from app.background.queue import BackgroundQueue, RedisBackgroundQueue
from app.infrastructure.redis.client import redis_client
from app.ingestion.service import IngestionService
from app.retrieval.retriever import ProjectRetriever
from app.retrieval.service import RetrievalService
from app.query.service import QueryService
from app.query.query_engine import QueryEngine
from app.core.composition import build_ingestion_service



def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


DBSession = Annotated[Session, Depends(get_db)]


def get_ingestion_queue() -> BackgroundQueue:
    return RedisBackgroundQueue(redis_client)

def get_ingestion_service(
    db: DBSession,
) -> IngestionService:
    return build_ingestion_service(db)

def get_project_retriever() -> ProjectRetriever:
    return ProjectRetriever()

def get_retrieval_service(
    db: DBSession,
    retriever: ProjectRetriever = Depends(get_project_retriever),
) -> RetrievalService:
    return RetrievalService(
        session=db,
        retriever=retriever,
    )

def get_query_engine(
    retriever: ProjectRetriever = Depends(get_project_retriever),
) -> QueryEngine:
    return QueryEngine(
        retriever=retriever,
    )

def get_query_service(
    db: DBSession,
    query_engine: QueryEngine = Depends(get_query_engine),
) -> QueryService:
    return QueryService(
        session=db,
        query_engine=query_engine,
    )
