from llama_index.core import StorageContext

from app.providers.vector_store import vector_store

storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
)