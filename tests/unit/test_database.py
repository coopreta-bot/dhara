from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import FastAPI

from rag import database


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


class FakeSessionContext:
    def __init__(self, session: object) -> None:
        self.session = session
        self.closed = False

    async def __aenter__(self) -> object:
        return self.session

    async def __aexit__(self, *_: object) -> None:
        self.closed = True


def test_database_lifespan_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(database.DATABASE_URL_ENV, raising=False)

    async def start_app() -> None:
        async with database.database_lifespan(FastAPI()):
            pytest.fail("Lifespan must not start without a database URL")

    with pytest.raises(RuntimeError, match=database.DATABASE_URL_ENV):
        asyncio.run(start_app())


def test_database_lifespan_disposes_engine_on_shutdown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = FastAPI()
    engine = FakeEngine()
    factory = object()
    monkeypatch.setenv(
        database.DATABASE_URL_ENV,
        "postgresql+asyncpg://localhost:5432/dhara",
    )
    monkeypatch.setattr(
        database,
        "create_async_engine",
        lambda url, *, pool_pre_ping: engine,
    )
    monkeypatch.setattr(
        database,
        "async_sessionmaker",
        lambda received_engine, *, expire_on_commit: factory,
    )

    async def exercise_lifespan() -> None:
        async with database.database_lifespan(app):
            assert app.state.db_engine is engine
            assert app.state.db_session_factory is factory
        assert engine.disposed

    asyncio.run(exercise_lifespan())
    assert not hasattr(app.state, database.ENGINE_STATE_KEY)
    assert not hasattr(app.state, database.SESSION_FACTORY_STATE_KEY)


def test_get_session_closes_session_after_dependency_exit() -> None:
    session = object()
    session_context = FakeSessionContext(session)
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(db_session_factory=lambda: session_context),
        ),
    )

    async def exercise_dependency() -> None:
        dependency = database.get_session(request)
        assert await anext(dependency) is session
        await dependency.aclose()

    asyncio.run(exercise_dependency())
    assert session_context.closed


def test_get_session_requires_active_lifespan() -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))

    async def start_dependency() -> None:
        await anext(database.get_session(request))

    with pytest.raises(RuntimeError, match="lifespan is not active"):
        asyncio.run(start_dependency())
