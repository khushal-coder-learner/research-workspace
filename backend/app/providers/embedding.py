from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.core.config import settings

from time import perf_counter

start_time = perf_counter()

embedding_model = HuggingFaceEmbedding(
    model_name=settings.embedding_model,
    local_files_only=True
)

print(perf_counter() - start_time)