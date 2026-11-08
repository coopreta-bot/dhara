"""Async database lifecycle and per-request session dependency for the RAG API."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL_ENV = "DHARA_DATABASE_URL"
SESSION_FACTORY_STATE_KEY = "db_session_factory"
ENGINE_STATE_KEY = "db_engine"


def _get_database_url() -> str:
    database_url = os.environ.get(DATABASE_URL_ENV)
    if not database_url:
        raise RuntimeError(f"{DATABASE_URL_ENV} must be set before starting the API")
    if not database_url.startswith("postgresql+asyncpg://"):
        raise RuntimeError(f"{DATABASE_URL_ENV} must use the postgresql+asyncpg:// driver URL")
    return database_url


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create the async engine at startup and dispose it during application shutdown."""
    engine: AsyncEngine = create_async_engine(
        _get_database_url(),
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    setattr(app.state, ENGINE_STATE_KEY, engine)
    setattr(app.state, SESSION_FACTORY_STATE_KEY, session_factory)

    try:
        yield
    finally:
        try:
            await engine.dispose()
        finally:
            delattr(app.state, SESSION_FACTORY_STATE_KEY)
            delattr(app.state, ENGINE_STATE_KEY)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one request-scoped session; callers own transaction boundaries."""
    session_factory: async_sessionmaker[AsyncSession] | None = getattr(
        request.app.state,
        SESSION_FACTORY_STATE_KEY,
        None,
    )
    if session_factory is None:
        raise RuntimeError("Database lifespan is not active; pass database_lifespan to FastAPI")

    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
