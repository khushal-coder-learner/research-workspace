# Research Workspace

Research Workspace is a production-oriented RAG playground for computer science papers. The current backend lets you:

- upload PDF papers into a project
- store metadata in PostgreSQL
- queue ingestion work in Redis
- parse, chunk, embed, and index documents with LlamaIndex
- ask project-scoped questions and receive grounded answers

The codebase is organized around business capabilities such as `projects`, `documents`, `ingestion`, `retrieval`, and `query` rather than a generic service/repository layering.

## Architecture

```mermaid
flowchart TD
    Client[Browser / API client] --> API[FastAPI app<br/>backend/app/main.py]

    API --> Projects[Projects API]
    API --> Documents[Documents API]
    API --> Query[Query API]

    Documents --> Disk[(Local PDF storage<br/>backend/storage/documents)]
    Documents --> Queue[(Redis ingestion queue)]
    Documents --> DB[(PostgreSQL + pgvector)]

    Queue --> Worker[Background ingestion worker]
    Worker --> Reader[PyMuPDF reader]
    Worker --> Pipeline[LlamaIndex ingestion pipeline]
    Pipeline --> Store[(PostgreSQL + pgvector)]

    Query --> Retriever[Project retriever]
    Retriever --> Store
    Query --> LLM[OpenRouter LLM]

    API --> DB
```

### Runtime Flow

1. A PDF is uploaded through the documents API.
2. The file is saved locally under `backend/storage/documents`.
3. A document row is created in PostgreSQL and a job is pushed to Redis.
4. The background worker picks up the job, reads the PDF, enriches metadata, chunks the text, embeds nodes, and writes them into pgvector.
5. The query endpoint builds a retriever for the selected project and synthesizes an answer with the configured LLM.

## Repository Layout

- `backend/app/main.py` FastAPI application entrypoint.
- `backend/app/projects` project CRUD and schemas.
- `backend/app/documents` document upload, listing, and lookup.
- `backend/app/ingestion` PDF ingestion pipeline and storage helpers.
- `backend/app/retrieval` project-scoped retrieval logic.
- `backend/app/query` question-answering orchestration.
- `backend/app/background` Redis queue and ingestion worker.
- `backend/app/infrastructure` database and Redis clients.
- `backend/storage/documents` local PDF storage used at runtime.
- `frontend/` currently exists as a placeholder, but there is no frontend app checked in yet.

## Requirements

- Python 3.12 or newer
- `uv`
- Docker and Docker Compose
- PostgreSQL 18 with `pgvector`
- Redis 8

## Environment Variables

Copy `.env.example` to `.env` and fill in your local values.

Important settings:

- `DATABASE_URL` SQLAlchemy connection string used by the app and Alembic
- `REDIS_URL` Redis connection string used by the background queue
- `POSTGRES_*` values used by the vector store and Docker Compose
- `GOOGLE_API_KEY` kept for future ingestion or model integrations
- `OPENROUTER_API_KEY` used by the query LLM
- `EMBEDDING_MODEL` Hugging Face embedding model name
- `GENERATION_MODEL` OpenRouter model name for answer generation
- `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_TOKENS`, and `TEMPERATURE` for retrieval and generation tuning

## Run Locally

### 1. Start PostgreSQL and Redis

From the repository root:

```powershell
docker compose up -d
```

This starts the `pgvector` PostgreSQL container and Redis on the default local ports.

### 2. Configure the backend

From `backend/`, install dependencies and prepare the environment:

```powershell
uv sync
```

Make sure `backend/.env` exists and contains valid values for `DATABASE_URL`, `REDIS_URL`, and your API keys.

### 3. Run migrations

From `backend/`:

```powershell
uv run alembic upgrade head
```

### 4. Start the API

From `backend/`:

```powershell
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the interactive API docs at:

- `http://localhost:8000/docs`

### 5. Start the ingestion worker

Run this in a second terminal from `backend/`:

```powershell
uv run python -m app.background.worker
```

The worker must be running if you want uploaded PDFs to move from `QUEUED` to `INDEXED`.

## Main API Endpoints

- `GET /` health-style root response
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `POST /documents/upload`
- `GET /projects/{project_id}/documents`
- `GET /documents/{document_id}`
- `POST /projects/{project_id}/query`

## Notes

- The application is optimized for RAG experimentation, not generic CRUD.
- Business logic lives in services; routers stay thin.
- Infrastructure code is isolated under `app/infrastructure` and `app/providers`.
- Secrets, local databases, PDFs, caches, and virtual environments are ignored by default through `.gitignore`.
