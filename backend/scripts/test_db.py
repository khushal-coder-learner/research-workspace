from sqlalchemy import text

from app.infrastructure.database.session import SessionLocal

with SessionLocal() as session:
    result = session.execute(text("SELECT 1"))

    print(result.scalar())