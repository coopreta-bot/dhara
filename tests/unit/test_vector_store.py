from __future__ import annotations

import asyncio
import hashlib
import json
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

import pytest

from rag.ingestion.pipeline import ingest_corpus
from rag.vector_store.loader import ChunkValidationError, load_staged_chunks
from rag.vector_store.migrate import migration_files, sql_statements

TENANT_ID = "00000000-0000-0000-0000-000000000003"


class RecordingSession:
    def __init__(self) -> None:
        self.executed: list[tuple[object, dict[str, object]]] = []
        self.in_transaction = False

    @asynccontextmanager
    async def begin(self):
        self.in_transaction = True
        try:
            yield
        finally:
            self.in_transaction = False

    async def execute(self, statement: object, parameters: dict[str, object]) -> None:
        assert self.in_transaction
        self.executed.append((statement, parameters))


def stage_chunks(tmp_path: Path) -> tuple[Path, Path]:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_id": "government-schemes",
                "dataset_version": "2026-11-08",
                "corpus": "government_schemes",
                "tenant_id": TENANT_ID,
                "consent": {
                    "record_id": "public-data-record-001",
                    "recorded_at": "2026-11-01",
                },
                "retention": {
                    "record_id": "retention-public-001",
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
    (input_dir / "scheme-001.json").write_text(
        json.dumps(
            {
                "document_id": "scheme-001",
                "source_doc_type": "government_scheme",
                "source_ref": "nabard/scheme-001",
                "title": "Scheme notice",
                "as_of_date": "2026-10-01",
                "content": "Eligible applicants should retain the scheme notice.",
            }
        ),
        encoding="utf-8",
    )
    ingest_corpus(manifest_path, input_dir, output_dir)
    return output_dir / "chunks.jsonl", output_dir / "ingestion-receipt.json"


def test_load_staged_chunks_upserts_a_consent_validated_corpus(tmp_path: Path) -> None:
    chunks_path, receipt_path = stage_chunks(tmp_path)
    session = RecordingSession()

    result = asyncio.run(
        load_staged_chunks(
            session,
            chunks_path,
            receipt_path,
            on_date=date(2026, 11, 8),
        )
    )

    assert result.chunk_count == 1
    assert result.dataset_id == "government-schemes"
    assert result.dataset_version == "2026-11-08"
    assert len(session.executed) == 2
    parameters = session.executed[0][1]
    assert parameters["tenant_id"] == TENANT_ID
    assert parameters["consent_record_id"] == "public-data-record-001"
    assert parameters["retention_expires_at"] == "2027-11-01"
    assert parameters["content"] == "Eligible applicants should retain the scheme notice."
    assert session.executed[1][1]["source_chunk_ids"] == [parameters["source_chunk_id"]]


def test_loader_rejects_an_expired_retention_record_before_starting_a_transaction(
    tmp_path: Path,
) -> None:
    chunks_path, receipt_path = stage_chunks(tmp_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["retention_expires_at"] = "2026-11-07"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    session = RecordingSession()

    with pytest.raises(ChunkValidationError, match="retention record has expired"):
        asyncio.run(
            load_staged_chunks(
                session,
                chunks_path,
                receipt_path,
                on_date=date(2026, 11, 8),
            )
        )

    assert not session.executed
    assert not session.in_transaction


def test_loader_rejects_unredacted_pii_in_a_staged_chunk(tmp_path: Path) -> None:
    chunks_path, receipt_path = stage_chunks(tmp_path)
    chunk = json.loads(chunks_path.read_text(encoding="utf-8"))
    chunk["content"] = "Call 9876543210 before delivery."
    chunk["content_sha256"] = hashlib.sha256(chunk["content"].encode("utf-8")).hexdigest()
    chunks_path.write_text(json.dumps(chunk) + "\n", encoding="utf-8")
    session = RecordingSession()

    with pytest.raises(ChunkValidationError, match="content contains unredacted PHONE_NUMBER"):
        asyncio.run(
            load_staged_chunks(
                session,
                chunks_path,
                receipt_path,
                on_date=date(2026, 11, 8),
            )
        )

    assert not session.executed


def test_initial_migration_creates_a_partial_pgvector_index() -> None:
    migrations = migration_files()
    migration = next(path for path in migrations if path.name == "0001_rag_chunks.sql")
    statements = list(sql_statements(migration.read_text(encoding="utf-8")))
    joined = "\n".join(statements)

    assert "CREATE EXTENSION IF NOT EXISTS vector" in joined
    assert "embedding VECTOR(1024)" in joined
    assert "UNIQUE (tenant_id, source_chunk_id)" in joined
    assert "WHERE embedding IS NOT NULL" in joined
