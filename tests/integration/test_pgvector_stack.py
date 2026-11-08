"""Opt-in integration check for the local self-hosted pgvector environment."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from rag.database import _get_database_url
from rag.ingestion.pipeline import ingest_corpus
from rag.vector_store.loader import load_staged_chunks
from rag.vector_store.migrate import apply_migrations

pytestmark = pytest.mark.skipif(
    os.environ.get("DHARA_RUN_PGVECTOR_INTEGRATION") != "1",
    reason="requires the local pgvector Compose service and explicit opt-in",
)


def test_local_pgvector_stack_migrates_and_loads_a_staged_corpus(tmp_path: Path) -> None:
    """Exercise extensions, migration, and the consent-validating loader together."""
    asyncio.run(_exercise_stack(tmp_path))


async def _exercise_stack(tmp_path: Path) -> None:
    tenant_id = str(uuid4())
    chunks_path, receipt_path = _stage_corpus(tmp_path, tenant_id)

    await apply_migrations()
    engine = create_async_engine(_get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            result = await load_staged_chunks(session, chunks_path, receipt_path)
        assert result.chunk_count == 1

        async with session_factory() as session:
            extension_name = await session.scalar(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            row_count = await session.scalar(
                text(
                    "SELECT count(*) FROM rag_chunks " "WHERE tenant_id = CAST(:tenant_id AS UUID)"
                ),
                {"tenant_id": tenant_id},
            )
            await session.rollback()
        assert extension_name == "vector"
        assert row_count == 1
    finally:
        async with session_factory() as session:
            async with session.begin():
                await session.execute(
                    text("DELETE FROM rag_chunks WHERE tenant_id = CAST(:tenant_id AS UUID)"),
                    {"tenant_id": tenant_id},
                )
        await engine.dispose()


def _stage_corpus(tmp_path: Path, tenant_id: str) -> tuple[Path, Path]:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_id": "pgvector-integration",
                "dataset_version": "2026-11-08",
                "corpus": "government_schemes",
                "tenant_id": tenant_id,
                "consent": {
                    "record_id": "public-data-record-integration",
                    "recorded_at": "2026-11-01",
                },
                "retention": {
                    "record_id": "retention-integration",
                    "expires_at": "2027-11-01",
                },
                "provenance": {
                    "kind": "public",
                    "system": "nabard",
                    "terms_ref": "nabard-terms",
                    "retrieved_at": "2026-11-08",
                },
            }
        ),
        encoding="utf-8",
    )
    (input_dir / "scheme.json").write_text(
        json.dumps(
            {
                "document_id": "scheme-integration",
                "source_doc_type": "government_scheme",
                "source_ref": "nabard/integration-scheme",
                "as_of_date": "2026-10-01",
                "content": "Eligible applicants should retain the scheme notice.",
            }
        ),
        encoding="utf-8",
    )
    ingest_corpus(manifest_path, input_dir, output_dir)
    return output_dir / "chunks.jsonl", output_dir / "ingestion-receipt.json"
