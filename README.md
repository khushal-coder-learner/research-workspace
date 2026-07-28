# Research Workspace

A production-oriented AI research platform for exploring computer science papers using Retrieval-Augmented Generation (RAG).

## Goals

- Upload research papers
- Index papers using LlamaIndex
- Ask questions across multiple papers
- Receive grounded answers with citations
- Experiment with different retrieval strategies

## Tech Stack

- FastAPI
- LlamaIndex
- PostgreSQL + pgvector
- Redis
- React
- Docker

## Background ingestion

Run the API and the ingestion worker as separate processes. From `backend/`:

```powershell
python -m app.background.worker
```
