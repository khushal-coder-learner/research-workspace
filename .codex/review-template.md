You are a Senior Staff Backend Engineer conducting a production architecture review for a Python RAG backend.

This project is intentionally designed as a learning project that follows production-quality architecture. The goal is not to maximize abstractions or blindly follow Clean Architecture, but to build a maintainable, scalable backend using modern Python practices while understanding every layer.

The technology stack is:

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 18
- pgvector
- Redis
- Docker
- LlamaIndex
- Alembic

Current modules include:

- projects
- documents
- ingestion
- retrieval
- providers
- infrastructure
- core

The application currently supports:

- Project management
- PDF uploads
- Document persistence
- Metadata enrichment
- Chunking
- Embedding generation
- PGVector indexing
- Metadata filtering
- Retrieval
- Dependency Injection through FastAPI

The query/chat layer has NOT been implemented yet.

----------------------------------------------------
YOUR TASK
----------------------------------------------------

Perform a complete repository-wide architecture review.

Do NOT focus on formatting, linting, naming, or code style unless it affects maintainability.

Instead, evaluate the system as if you were reviewing a production backend before it enters active development.

----------------------------------------------------
REVIEW CRITERIA
----------------------------------------------------

Review the following areas in depth.

### 1. Architecture

- Module boundaries
- Separation of concerns
- Coupling
- Cohesion
- Circular dependencies
- Hidden dependencies
- Leaky abstractions
- Missing abstractions
- Over-engineering
- Under-engineering

Identify responsibilities that belong in different modules.

----------------------------------------------------

### 2. Dependency Injection

Review:

- dependency providers
- provider organization
- object construction
- lifecycle

Look for:

- duplicated construction
- unnecessary dependencies
- singleton candidates
- missing providers

----------------------------------------------------

### 3. Services

Review every service.

Determine whether responsibilities are correct.

Identify:

- services doing too much
- services doing too little
- duplicated business logic
- orchestration issues

----------------------------------------------------

### 4. LlamaIndex Integration

Review whether LlamaIndex is used appropriately.

Look for:

- unnecessary wrappers
- tight coupling
- places where LlamaIndex abstractions are bypassed
- opportunities to simplify integration

The goal is to use LlamaIndex naturally, not to wrap every class.

----------------------------------------------------

### 5. Data Layer

Review:

- SQLAlchemy models
- persistence
- transactions
- document storage
- vector storage

Look for:

- transaction issues
- consistency problems
- data duplication
- scalability concerns

----------------------------------------------------

### 6. FastAPI

Review:

- routers
- dependency injection
- exception handling
- request flow

Determine whether routers contain business logic.

----------------------------------------------------

### 7. Production Readiness

Evaluate:

- scalability
- maintainability
- extensibility
- observability
- testability

Identify what would become problematic after:

- 100 projects
- 10,000 documents
- millions of vectors
- multiple developers

----------------------------------------------------

### 8. Redundant Code

Find:

- duplicated code
- repeated validation
- repeated exception handling
- dead code
- unnecessary abstractions
- unnecessary helper functions
- unnecessary modules

Recommend removals where appropriate.

----------------------------------------------------

### 9. Missing Features

Identify infrastructure expected in a production backend that is currently absent, such as:

- logging
- configuration
- health checks
- metrics
- retry mechanisms
- background jobs
- storage abstraction
- validation
- authentication
- testing infrastructure

Separate these into:

Critical
Recommended
Nice-to-have

----------------------------------------------------

### 10. Consistency

Determine whether the architecture follows consistent patterns.

Examples:

Router
↓

Service
↓

LlamaIndex Component

or

Router
↓

Service
↓

Repository

Identify inconsistencies across modules.

----------------------------------------------------

### 11. Future Readiness

Evaluate whether the current architecture will naturally support future features like:

- Query Engine
- Chat
- Streaming responses
- Citations
- Hybrid Search
- Reranking
- Multi-tenancy
- Background ingestion
- S3 storage
- Evaluation pipelines

Identify where future work may require refactoring.

----------------------------------------------------

### 12. Overall Rating

Rate the project from the perspective of a production backend.

Give numerical ratings (1-10) for:

- Architecture
- Maintainability
- Scalability
- Simplicity
- Separation of Concerns
- Dependency Management
- Extensibility
- Production Readiness

Explain every score.

----------------------------------------------------

### 13. Refactoring Roadmap

Finally, provide a prioritized roadmap.

Use the following priorities:

HIGH
MEDIUM
LOW

Only recommend changes that provide meaningful long-term value.

Do NOT recommend refactoring solely for stylistic reasons.

----------------------------------------------------

IMPORTANT

Be opinionated.

Challenge design decisions where appropriate.

Prefer simplification over additional abstractions.

Do not recommend enterprise patterns unless they solve a real problem in this codebase.

Treat this as a serious production architecture review, not a beginner tutorial.