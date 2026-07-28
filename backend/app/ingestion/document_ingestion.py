from pathlib import Path
from uuid import UUID
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.storage import StorageContext
from llama_index.core.embeddings import BaseEmbedding

from app.ingestion.metadata import enrich_documents


class DocumentIngestion:
    """Coordinates the ingestion of a PDF into the vector store."""

    def __init__(
        self,
        *,
        reader: PyMuPDFReader,
        storage_context: StorageContext,
        embed_model: BaseEmbedding,
        transformations: list[Any],
    ):
        
        self._pipeline = IngestionPipeline(
            transformations=transformations,
        )

        self._reader = reader

        self._storage_context = storage_context
        self._embed_model = embed_model

    def ingest(
        self,
        pdf_path: Path,
        *,
        project_id: UUID,
        document_id: UUID,
        filename: str,
    ) -> None:
        documents = self._reader.load_data(pdf_path)

        documents = enrich_documents(
            documents,
            project_id=project_id,
            document_id=document_id,
            filename=filename,
        )

        index = VectorStoreIndex.from_vector_store(
            vector_store=self._storage_context.vector_store,
            storage_context=self._storage_context, 
            embed_model=self._embed_model,
        )

        index.delete_ref_doc(str(document_id))

        nodes = self._pipeline.run(documents=documents)

        index.insert_nodes(nodes)
