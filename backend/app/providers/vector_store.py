from llama_index.vector_stores.postgres import PGVectorStore

from app.core.config import settings


vector_store = PGVectorStore.from_params(
    database=settings.postgres_db,
    host=settings.postgres_host,
    password=settings.postgres_password,
    port=settings.postgres_port,
    user=settings.postgres_user,

    table_name="research_chunks",

    embed_dim=settings.embed_dimensions,

    hybrid_search=False,
)