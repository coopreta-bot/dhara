# rag

Self-hosted retrieval. Vector store is Postgres + pgvector, or Qdrant/Milvus later. No managed vector API.

Status: OPEN. This folder contains the Phase 0 scaffold and initial Phase 1
database-lifecycle wiring. No RAG service is LIVE VERIFIED.

## Async database wiring

`database.py` provides a FastAPI lifespan that creates and disposes an async
SQLAlchemy engine, plus `get_session` / `SessionDep` for a request-scoped
`AsyncSession`. Set `DHARA_DATABASE_URL` to a `postgresql+asyncpg://` URL before
starting an app with `FastAPI(lifespan=database_lifespan)`. Do not commit the
URL or credentials.

The dependency closes the session but does not commit. Routes or services must
set explicit transaction boundaries. This wiring does not start Postgres, apply
`docs/architecture/schema.sql`, create migrations, or implement the RAG API;
those capabilities remain OPEN.

`app.py` attaches that lifespan to the `rag.app:app` FastAPI application and
implements `GET /health`. It runs `SELECT 1` through the request-scoped
session, returning HTTP 200 only when that check succeeds; HTTP 503 reports
that the database remains OPEN. Retrieval and `POST /query` are not
implemented.
