"""FastAPI application foundation for the self-hosted RAG service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from rag.database import SessionDep, database_lifespan


def create_app() -> FastAPI:
    """Create the RAG API with its database lifecycle attached."""
    app = FastAPI(
        title="Coopreta Dhara RAG API",
        version="0.0.0",
        lifespan=database_lifespan,
    )

    @app.get("/health", tags=["operations"])
    async def health(session: SessionDep) -> dict[str, object]:
        """Report database readiness without exposing database or error details."""
        try:
            await session.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "OPEN",
                    "checks": {
                        "database": "OPEN",
                        "rag": "OPEN",
                    },
                },
            ) from error

        return {
            "status": "OPEN",
            "checks": {
                "database": "PASS",
                "rag": "OPEN",
            },
        }

    return app


app = create_app()
