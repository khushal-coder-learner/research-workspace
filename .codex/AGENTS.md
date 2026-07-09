# AGENTS.md

# Research Workspace — AI Engineering Guide

## Purpose

This repository contains a production-oriented Research Workspace for exploring
computer science research papers using Retrieval-Augmented Generation (RAG).

The primary goal of this project is **learning production RAG architecture with
LlamaIndex**, not simply building an application.

The application exists to support experimentation with ingestion, retrieval,
generation, evaluation and agentic workflows.

When there is a trade-off between:

- application features
- RAG architecture

always prioritize the RAG architecture.


-------------------------------------------------------------------------------

# Technology Stack

## Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL 18
- pgvector
- Redis
- LlamaIndex
- uv

## Frontend

- React
- TypeScript
- Vite

## Infrastructure

- Docker Compose


-------------------------------------------------------------------------------

# Project Structure

The project is organized by **business capability**, not technical layer.

Never create global folders like:

- services/
- repositories/
- routers/
- models/
- schemas/

Each business capability owns its own implementation.

Current structure:

backend/

    app/

        core/

        infrastructure/

            database/

            redis/

        projects/

        documents/

        ingestion/

        retrieval/

        research/

        main.py


-------------------------------------------------------------------------------

# Architecture Principles

## Domain-oriented organization

Every feature owns its own:

- router
- service
- schemas
- models

Example:

projects/

    router.py

    service.py

    schemas.py

    models.py


-------------------------------------------------------------------------------

## Infrastructure isolation

Infrastructure code belongs only inside

app/infrastructure/

Examples:

- SQLAlchemy engine
- Session management
- Redis client
- LlamaIndex integrations
- Vector store integrations

Business modules must never create infrastructure.


-------------------------------------------------------------------------------

## Thin routers

FastAPI routers should only

- validate requests
- call services
- return responses

Business logic belongs inside services.

Routers should never implement business rules.


-------------------------------------------------------------------------------

## DTO separation

Never expose SQLAlchemy ORM models through the API.

Always use Pydantic DTOs.

ORM models represent persistence.

DTOs represent API contracts.


-------------------------------------------------------------------------------

## SQLAlchemy

Always use SQLAlchemy 2.0 style.

Use:

- Mapped
- mapped_column
- select()

Never use

session.query(...)

Prefer typed ORM models.


-------------------------------------------------------------------------------

## Configuration

Application configuration is accessed only through

settings

Never use

os.getenv()

inside business modules.


-------------------------------------------------------------------------------

## Dependency Injection

Use FastAPI dependency injection.

Avoid global state whenever practical.

Singleton resources such as

- Engine
- Redis client

may exist globally.


-------------------------------------------------------------------------------

# Coding Standards

## Type Hints

Every public function should use type hints.

Avoid Any unless unavoidable.


-------------------------------------------------------------------------------

## Functions

Keep functions focused.

One responsibility.

Prefer explicit code over clever abstractions.


-------------------------------------------------------------------------------

## Classes

Classes should represent meaningful domain concepts.

Avoid unnecessary inheritance.

Prefer composition.


-------------------------------------------------------------------------------

## Comments

Avoid comments that explain obvious code.

Write code that is self-explanatory.

Only comment architectural decisions or non-obvious behavior.


-------------------------------------------------------------------------------

## Naming

Use descriptive names.

Prefer

create_project()

over

create()

Prefer

ResearchService

over

Manager


-------------------------------------------------------------------------------

## Error Handling

Raise meaningful exceptions.

Avoid returning None for exceptional situations.

Prefer explicit failure.



-------------------------------------------------------------------------------

## Logging

Use structured logging.

Avoid print() inside application code.


-------------------------------------------------------------------------------

## Testing

Every important business behavior should eventually have tests.

Infrastructure does not need exhaustive tests during MVP.

Focus testing effort on RAG components.


-------------------------------------------------------------------------------

# Current Infrastructure

Already implemented:

✓ FastAPI initialization

✓ Settings management

✓ PostgreSQL

✓ Redis

✓ SQLAlchemy engine

✓ Session factory

✓ Declarative Base

✓ Alembic

✓ Docker Compose

✓ Project model

✓ Initial database migration


-------------------------------------------------------------------------------

# Current Database

projects

- id
- name
- description
- created_at
- updated_at


-------------------------------------------------------------------------------

# Current Priorities

Highest priority:

1. RAG ingestion pipeline
2. Retrieval architecture
3. Query Engine
4. Evaluation
5. Agentic workflows

Application CRUD is considered commodity work and may be delegated to AI.


-------------------------------------------------------------------------------

# LlamaIndex Philosophy

LlamaIndex is an implementation detail.

The architecture should remain understandable without knowledge of any
specific framework.

Avoid coupling business logic directly to LlamaIndex abstractions whenever
possible.

Wrap framework-specific code inside infrastructure or dedicated RAG modules.


-------------------------------------------------------------------------------

# AI Agent Instructions

When implementing features:

1. Preserve the project structure.

2. Do not reorganize files.

3. Do not introduce new architectural patterns without justification.

4. Do not introduce generic repository patterns.

5. Do not introduce generic CRUD base classes.

6. Keep implementations straightforward.

7. Follow existing naming conventions.

8. Respect module boundaries.

9. Do not modify infrastructure unless explicitly requested.

10. Prefer readability over cleverness.


-------------------------------------------------------------------------------

# Implementation Workflow

Every implementation should follow this order.

Understand the task.

↓

Respect existing architecture.

↓

Implement the minimum correct solution.

↓

Keep code simple.

↓

Do not introduce speculative abstractions.

↓

Explain important design decisions.


-------------------------------------------------------------------------------

# Engineering Philosophy

This repository is primarily a learning project.

Learning objectives take precedence over feature count.

When implementing RAG functionality:

- optimize for understanding
- optimize for experimentation
- optimize for architectural clarity

When implementing boilerplate:

- optimize for correctness
- optimize for maintainability
- avoid unnecessary complexity

Every architectural decision should be explainable in plain English.

If a design cannot be explained simply,
it is probably too complicated.

### FastAPI Conventions

- Shared dependencies (for example `get_db`) belong in `app.core.dependencies`.
- Routers should return domain objects directly whenever `response_model` with Pydantic's `from_attributes=True` can perform the serialization.
- Services should not depend on FastAPI-specific classes such as `HTTPException`. Raise domain exceptions instead, and let the API layer translate them into HTTP responses.