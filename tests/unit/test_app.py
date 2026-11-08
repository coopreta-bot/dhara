from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from rag import app as rag_app
from rag import database


class ReadySession:
    async def execute(self, statement: Any) -> None:
        assert str(statement) == "SELECT 1"


class UnavailableSession:
    async def execute(self, statement: Any) -> None:
        raise SQLAlchemyError("database is unavailable")


async def ready_session() -> ReadySession:
    yield ReadySession()


async def unavailable_session() -> UnavailableSession:
    yield UnavailableSession()


def test_health_reports_database_readiness(monkeypatch) -> None:
    monkeypatch.setenv(
        database.DATABASE_URL_ENV,
        "postgresql+asyncpg://localhost:5432/dhara",
    )
    rag_app.app.dependency_overrides[database.get_session] = ready_session

    try:
        with TestClient(rag_app.app) as client:
            response = client.get("/health")
    finally:
        rag_app.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "status": "OPEN",
        "checks": {
            "database": "PASS",
            "rag": "OPEN",
        },
    }


def test_health_returns_service_unavailable_for_database_error(monkeypatch) -> None:
    monkeypatch.setenv(
        database.DATABASE_URL_ENV,
        "postgresql+asyncpg://localhost:5432/dhara",
    )
    rag_app.app.dependency_overrides[database.get_session] = unavailable_session

    try:
        with TestClient(rag_app.app) as client:
            response = client.get("/health")
    finally:
        rag_app.app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "status": "OPEN",
            "checks": {
                "database": "OPEN",
                "rag": "OPEN",
            },
        },
    }
