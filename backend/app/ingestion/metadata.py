from __future__ import annotations

from uuid import UUID

from llama_index.core.schema import Document


def enrich_documents(
    documents: list[Document],
    *,
    project_id: UUID,
    document_id: UUID,
    filename: str,
) -> list[Document]:
    """
    Enrich LlamaIndex documents with application metadata.

    This metadata is inherited by every TextNode produced during chunking and
    ultimately persisted in the vector store.
    """
    for document in documents:
        # Stable identity for document lifecycle management
        document.id_ = str(document_id)
        
        document.metadata.update(
            {
                "project_id": str(project_id),
                "document_id": str(document_id),
                "filename": filename,
                "page_number": int(document.metadata.get("source", 0)),
            }
        )

        # Remove metadata that isn't useful for retrieval
        document.metadata.pop("file_path", None)
        document.metadata.pop("source", None)

    return documents