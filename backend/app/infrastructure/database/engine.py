from sqlalchemy import create_engine

from app.core.config import settings

from functools import lru_cache

@lru_cache
def get_engine():
    return create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)