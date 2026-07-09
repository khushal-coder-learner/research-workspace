from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.database.engine import get_engine

SessionLocal = sessionmaker(
    bind=get_engine(),
    class_=Session,
    autoflush=False,
    autocommit=False,
)