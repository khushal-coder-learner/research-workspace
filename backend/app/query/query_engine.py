from uuid import UUID

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer

from app.providers.llm import llm
from app.retrieval.retriever import ProjectRetriever
from app.query.prompts import qa_prompt


class QueryEngine:
    """LlamaIndex query engine for project-scoped question answering."""

    def __init__(
        self,
        retriever: ProjectRetriever,
    ) -> None:
        self._retriever = retriever

    def _build_query_engine(
        self,
        *,
        project_id: UUID,
        top_k: int,
    ) -> BaseQueryEngine:
        base_retriever: BaseRetriever = self._retriever.build(
            project_id=project_id,
            top_k=top_k,
        )

        response_synthesizer = get_response_synthesizer(
            llm=llm,
            text_qa_template=qa_prompt
        )

        return RetrieverQueryEngine(
            retriever=base_retriever,
            response_synthesizer=response_synthesizer,
        )

    def query(
        self,
        query: str,
        *,
        project_id: UUID,
        top_k: int = 5,
    ):
        query_engine = self._build_query_engine(
            project_id=project_id,
            top_k=top_k,
        )

        return query_engine.query(query)
    