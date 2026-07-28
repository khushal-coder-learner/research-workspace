from app.core.config import settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


embedding_model = HuggingFaceEmbedding(
    model_name=settings.embedding_model,
    local_files_only=True,
)
