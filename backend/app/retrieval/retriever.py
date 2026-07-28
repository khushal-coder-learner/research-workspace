from uuid import UUID

from llama_index.core import VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.schema import NodeWithScore

from app.providers.embedding import embedding_model
from app.providers.vector_store import vector_store
from app.retrieval.filters import project_filter


class ProjectRetriever:
    """Retrieve nodes belonging to a single project."""

    def __init__(self) -> None:
        self._index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embedding_model,
        )

    def build(
        self,
        *,
        project_id: UUID,
        top_k: int,
    ) -> BaseRetriever:
        return self._index.as_retriever(
            similarity_top_k=top_k,
            filters=project_filter(project_id),
        )

    def retrieve(
        self,
        query: str,
        *,
        project_id: UUID,
        top_k: int = 5,
    ) -> list[NodeWithScore]:
        retriever = self.build(
            project_id=project_id,
            top_k=top_k,
        )

        return retriever.retrieve(query)