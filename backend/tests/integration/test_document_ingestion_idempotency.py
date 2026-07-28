from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import fitz
import pytest
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.readers.file import PyMuPDFReader
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import delete

from app.documents.models import Document, DocumentStatus
from app.ingestion.document_ingestion import DocumentIngestion
from app.infrastructure.database.session import SessionLocal
from app.projects.models import Project
from app.providers.embedding import embedding_model
from app.providers.parser import parser
from app.core.config import settings


def _write_pdf(path: Path, text: str) -> None:
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_textbox(fitz.Rect(36, 36, 560, 806), text)
    pdf.save(path)
    pdf.close()


@pytest.fixture(scope="module")
def vector_store() -> PGVectorStore:
    store = PGVectorStore.from_params(
        database=settings.postgres_db,
        host=settings.postgres_host,
        password=settings.postgres_password,
        port=settings.postgres_port,
        user=settings.postgres_user,
        table_name=f"test_idempotency_{uuid4().hex[:12]}",
        embed_dim=settings.embed_dimensions,
        hybrid_search=False,
    )
    yield store
    store.clear()


@pytest.fixture
def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def document_fixture(session, tmp_path: Path):
    project_id = uuid4()
    document_id = uuid4()
    path = tmp_path / "document.pdf"
    _write_pdf(path, "original document content " * 80)

    project = Project(id=project_id, name=f"integration-{project_id}")
    document = Document(
        id=document_id,
        project_id=project_id,
        filename="document.pdf",
        file_path=str(path),
        status=DocumentStatus.UPLOADED,
    )
    project.documents.append(document)
    session.add(project)
    session.commit()
    session.refresh(document)

    try:
        yield document, path
    finally:
        session.execute(delete(Document).where(Document.id == document_id))
        session.execute(delete(Project).where(Project.id == project_id))
        session.commit()


@pytest.fixture
def ingestor(vector_store: PGVectorStore) -> DocumentIngestion:
    return DocumentIngestion(
        reader=PyMuPDFReader(),
        storage_context=StorageContext.from_defaults(vector_store=vector_store),
        embed_model=embedding_model,
        transformations=[parser, embedding_model],
    )


def _ingest(ingestor: DocumentIngestion, document: Document) -> None:
    ingestor.ingest(
        Path(document.file_path),
        project_id=document.project_id,
        document_id=document.id,
        filename=document.filename,
    )


def _nodes_for(store: PGVectorStore, document_id: UUID):
    return store.get_nodes(
        filters=MetadataFilters(
            filters=[
                MetadataFilter(key="document_id", value=str(document_id)),
            ]
        )
    )


def test_first_ingestion_writes_nodes_and_records_count(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
) -> None:
    document, _ = document_fixture

    _ingest(ingestor, document)

    node_count = len(_nodes_for(vector_store, document.id))
    assert node_count > 0


def test_reingestion_converges_to_original_node_count(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
) -> None:
    document, _ = document_fixture

    _ingest(ingestor, document)
    original_count = len(_nodes_for(vector_store, document.id))

    _ingest(ingestor, document)

    assert len(_nodes_for(vector_store, document.id)) == original_count


def test_multiple_repeated_ingestions_keep_node_count_constant(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
) -> None:
    document, _ = document_fixture

    _ingest(ingestor, document)
    original_count = len(_nodes_for(vector_store, document.id))

    for _ in range(4):
        _ingest(ingestor, document)

    assert len(_nodes_for(vector_store, document.id)) == original_count


def test_updated_file_replaces_old_nodes_for_same_document_uuid(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
) -> None:
    document, path = document_fixture
    old_text = "old version marker"
    new_text = "new version marker"

    _write_pdf(path, f"{old_text} " * 80)
    _ingest(ingestor, document)
    old_nodes = _nodes_for(vector_store, document.id)

    _write_pdf(path, f"{new_text} " * 80)
    _ingest(ingestor, document)
    new_nodes = _nodes_for(vector_store, document.id)

    assert new_nodes
    assert all(old_text not in node.get_content() for node in new_nodes)
    assert all(new_text in node.get_content() for node in new_nodes)
    old_contents = {old_node.get_content() for old_node in old_nodes}
    assert all(node.get_content() not in old_contents for node in new_nodes)


def test_reindexing_one_document_does_not_change_another(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    session,
    tmp_path: Path,
) -> None:
    project_id = uuid4()
    first_id = uuid4()
    second_id = uuid4()
    first_path = tmp_path / "first.pdf"
    second_path = tmp_path / "second.pdf"
    _write_pdf(first_path, "first document marker " * 80)
    _write_pdf(second_path, "second document marker " * 80)

    project = Project(id=project_id, name=f"integration-{project_id}")
    first = Document(
        id=first_id,
        project_id=project_id,
        filename="first.pdf",
        file_path=str(first_path),
    )
    second = Document(
        id=second_id,
        project_id=project_id,
        filename="second.pdf",
        file_path=str(second_path),
    )
    project.documents.extend([first, second])
    session.add(project)
    session.commit()

    try:
        _ingest(ingestor, first)
        _ingest(ingestor, second)
        second_before = [node.get_content() for node in _nodes_for(vector_store, second_id)]

        _write_pdf(first_path, "updated first document marker " * 80)
        _ingest(ingestor, first)

        assert [node.get_content() for node in _nodes_for(vector_store, second_id)] == second_before
    finally:
        session.execute(delete(Document).where(Document.id.in_([first_id, second_id])))
        session.execute(delete(Project).where(Project.id == project_id))
        session.commit()


def test_retry_after_failure_between_delete_and_insert_restores_one_version(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document, _ = document_fixture
    _ingest(ingestor, document)
    expected_contents = [node.get_content() for node in _nodes_for(vector_store, document.id)]

    original_insert_nodes = VectorStoreIndex.insert_nodes
    failed = False

    def fail_once(self, nodes, **kwargs):
        nonlocal failed
        if not failed:
            failed = True
            raise RuntimeError("insertion failure")
        return original_insert_nodes(self, nodes, **kwargs)

    monkeypatch.setattr(VectorStoreIndex, "insert_nodes", fail_once)
    with pytest.raises(RuntimeError, match="insertion failure"):
        _ingest(ingestor, document)

    assert _nodes_for(vector_store, document.id) == []

    _ingest(ingestor, document)
    final_nodes = _nodes_for(vector_store, document.id)
    assert [node.get_content() for node in final_nodes] == expected_contents
    assert len(final_nodes) == len(expected_contents)


def test_indexed_nodes_preserve_required_metadata(
    ingestor: DocumentIngestion,
    vector_store: PGVectorStore,
    document_fixture,
) -> None:
    document, _ = document_fixture
    _ingest(ingestor, document)

    for node in _nodes_for(vector_store, document.id):
        assert node.ref_doc_id == str(document.id)
        assert node.metadata["project_id"] == str(document.project_id)
        assert node.metadata["document_id"] == str(document.id)
        assert node.metadata["filename"] == document.filename
        assert "page_number" in node.metadata
