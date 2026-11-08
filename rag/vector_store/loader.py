"""Load consent-validated local RAG chunks into the self-hosted pgvector store."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from rag.database import _get_database_url
from rag.ingestion.pipeline import REDACTION_PATTERNS

EXPECTED_SCHEMA_VERSION = "1.0"

UPSERT_CHUNK = text("""
    INSERT INTO rag_chunks (
      tenant_id,
      source_chunk_id,
      dataset_id,
      dataset_version,
      corpus,
      consent_record_id,
      consent_recorded_at,
      retention_record_id,
      retention_expires_at,
      source_doc_type,
      source_ref,
      title,
      as_of_date,
      content,
      content_sha256,
      pii_redactions,
      provenance
    ) VALUES (
      CAST(:tenant_id AS UUID),
      :source_chunk_id,
      :dataset_id,
      :dataset_version,
      :corpus,
      :consent_record_id,
      CAST(:consent_recorded_at AS DATE),
      :retention_record_id,
      CAST(:retention_expires_at AS DATE),
      :source_doc_type,
      :source_ref,
      :title,
      CAST(:as_of_date AS DATE),
      :content,
      :content_sha256,
      CAST(:pii_redactions AS JSONB),
      CAST(:provenance AS JSONB)
    )
    ON CONFLICT (tenant_id, source_chunk_id) DO UPDATE SET
      dataset_id = EXCLUDED.dataset_id,
      dataset_version = EXCLUDED.dataset_version,
      corpus = EXCLUDED.corpus,
      consent_record_id = EXCLUDED.consent_record_id,
      consent_recorded_at = EXCLUDED.consent_recorded_at,
      retention_record_id = EXCLUDED.retention_record_id,
      retention_expires_at = EXCLUDED.retention_expires_at,
      source_doc_type = EXCLUDED.source_doc_type,
      source_ref = EXCLUDED.source_ref,
      title = EXCLUDED.title,
      as_of_date = EXCLUDED.as_of_date,
      content = EXCLUDED.content,
      content_sha256 = EXCLUDED.content_sha256,
      pii_redactions = EXCLUDED.pii_redactions,
      provenance = EXCLUDED.provenance,
      embedding = CASE
        WHEN rag_chunks.content_sha256 = EXCLUDED.content_sha256 THEN rag_chunks.embedding
        ELSE NULL
      END,
      updated_at = now()
    """)

DELETE_STALE_CHUNKS = text("""
    DELETE FROM rag_chunks
    WHERE tenant_id = CAST(:tenant_id AS UUID)
      AND dataset_id = :dataset_id
      AND dataset_version = :dataset_version
      AND source_chunk_id <> ALL(CAST(:source_chunk_ids AS TEXT[]))
    """)


class ChunkValidationError(ValueError):
    """Raised when staged chunks cannot safely enter the local vector store."""


@dataclass(frozen=True)
class LoadResult:
    """Number of rows accepted by a single atomic chunk load."""

    chunk_count: int
    dataset_id: str
    dataset_version: str


async def load_staged_chunks(
    session: AsyncSession,
    chunks_path: Path,
    receipt_path: Path,
    *,
    on_date: date | None = None,
) -> LoadResult:
    """Validate a staged corpus and atomically upsert it into ``rag_chunks``."""
    receipt = _load_receipt(receipt_path)
    validation_date = on_date or date.today()
    _validate_receipt(receipt, validation_date)
    chunks = list(_load_chunks(chunks_path))

    if receipt["chunk_count"] != len(chunks):
        raise ChunkValidationError("receipt.chunk_count does not match the staged chunk count")

    parameters = [_chunk_parameters(chunk, receipt) for chunk in chunks]
    source_chunk_ids = [parameter["source_chunk_id"] for parameter in parameters]
    if len(source_chunk_ids) != len(set(source_chunk_ids)):
        raise ChunkValidationError("staged chunks contain duplicate chunk.chunk_id values")

    async with session.begin():
        for parameter in parameters:
            await session.execute(UPSERT_CHUNK, parameter)
        await session.execute(
            DELETE_STALE_CHUNKS,
            {
                "tenant_id": receipt["tenant_id"],
                "dataset_id": receipt["dataset_id"],
                "dataset_version": receipt["dataset_version"],
                "source_chunk_ids": source_chunk_ids,
            },
        )

    return LoadResult(
        chunk_count=len(parameters),
        dataset_id=receipt["dataset_id"],
        dataset_version=receipt["dataset_version"],
    )


async def load_into_database(chunks_path: Path, receipt_path: Path) -> LoadResult:
    """Open the configured self-hosted database and load one staged corpus."""
    engine = create_async_engine(_get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            return await load_staged_chunks(session, chunks_path, receipt_path)
    finally:
        await engine.dispose()


def _load_receipt(receipt_path: Path) -> dict[str, Any]:
    return _load_json_object(receipt_path, "ingestion receipt")


def _load_chunks(chunks_path: Path) -> Iterable[dict[str, Any]]:
    try:
        lines = chunks_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise ChunkValidationError(f"chunk file does not exist: {chunks_path}") from error

    if not lines:
        raise ChunkValidationError("chunk file is empty")

    for line_number, line in enumerate(lines, start=1):
        try:
            chunk = json.loads(line)
        except json.JSONDecodeError as error:
            raise ChunkValidationError(f"chunk line {line_number} is not valid JSON") from error
        if not isinstance(chunk, dict):
            raise ChunkValidationError(f"chunk line {line_number} must be a JSON object")
        yield chunk


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ChunkValidationError(f"{label} does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise ChunkValidationError(f"{label} is not valid JSON: {path}") from error
    if not isinstance(payload, dict):
        raise ChunkValidationError(f"{label} must be a JSON object")
    return payload


def _validate_receipt(receipt: dict[str, Any], validation_date: date) -> None:
    if (
        _required_text(receipt.get("schema_version"), "receipt.schema_version")
        != EXPECTED_SCHEMA_VERSION
    ):
        raise ChunkValidationError("receipt.schema_version is not supported")

    for key in (
        "dataset_id",
        "dataset_version",
        "corpus",
        "consent_record_id",
        "retention_record_id",
    ):
        _required_text(receipt.get(key), f"receipt.{key}")

    _valid_uuid(receipt.get("tenant_id"), "receipt.tenant_id")
    consent_recorded_at = _valid_date(
        receipt.get("consent_recorded_at"), "receipt.consent_recorded_at"
    )
    retention_expires_at = _valid_date(
        receipt.get("retention_expires_at"), "receipt.retention_expires_at"
    )
    if consent_recorded_at > validation_date:
        raise ChunkValidationError("receipt.consent_recorded_at is in the future")
    if retention_expires_at < validation_date:
        raise ChunkValidationError("receipt retention record has expired")

    chunk_count = receipt.get("chunk_count")
    if not isinstance(chunk_count, int) or chunk_count <= 0:
        raise ChunkValidationError("receipt.chunk_count must be a positive integer")


def _chunk_parameters(chunk: dict[str, Any], receipt: dict[str, Any]) -> dict[str, object]:
    if (
        _required_text(chunk.get("schema_version"), "chunk.schema_version")
        != EXPECTED_SCHEMA_VERSION
    ):
        raise ChunkValidationError("chunk.schema_version is not supported")

    matching_keys = (
        "dataset_id",
        "dataset_version",
        "corpus",
        "tenant_id",
        "consent_record_id",
        "retention_record_id",
    )
    for key in matching_keys:
        value = _required_text(chunk.get(key), f"chunk.{key}")
        if value != receipt[key]:
            raise ChunkValidationError(f"chunk.{key} does not match the ingestion receipt")

    _valid_uuid(chunk["tenant_id"], "chunk.tenant_id")
    source_chunk_id = _required_text(chunk.get("chunk_id"), "chunk.chunk_id")
    source_doc_type = _required_text(chunk.get("source_doc_type"), "chunk.source_doc_type")
    source_ref = _required_text(chunk.get("source_ref"), "chunk.source_ref")
    title = _optional_text(chunk.get("title"), "chunk.title")
    content = _required_text(chunk.get("content"), "chunk.content")
    content_sha256 = _required_text(chunk.get("content_sha256"), "chunk.content_sha256")
    expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if content_sha256 != expected_hash:
        raise ChunkValidationError("chunk.content_sha256 does not match chunk.content")

    for label, value in (
        ("chunk.source_doc_type", source_doc_type),
        ("chunk.source_ref", source_ref),
        ("chunk.title", title),
        ("chunk.content", content),
    ):
        _reject_unredacted_pii(value, label)

    as_of_date = _optional_date(chunk.get("as_of_date"), "chunk.as_of_date")
    pii_redactions = chunk.get("pii_redactions")
    provenance = chunk.get("provenance")
    if not isinstance(pii_redactions, dict):
        raise ChunkValidationError("chunk.pii_redactions must be an object")
    if not isinstance(provenance, dict):
        raise ChunkValidationError("chunk.provenance must be an object")

    return {
        "tenant_id": chunk["tenant_id"],
        "source_chunk_id": source_chunk_id,
        "dataset_id": chunk["dataset_id"],
        "dataset_version": chunk["dataset_version"],
        "corpus": chunk["corpus"],
        "consent_record_id": chunk["consent_record_id"],
        "consent_recorded_at": receipt["consent_recorded_at"],
        "retention_record_id": chunk["retention_record_id"],
        "retention_expires_at": receipt["retention_expires_at"],
        "source_doc_type": source_doc_type,
        "source_ref": source_ref,
        "title": title,
        "as_of_date": as_of_date,
        "content": content,
        "content_sha256": content_sha256,
        "pii_redactions": json.dumps(pii_redactions, sort_keys=True),
        "provenance": json.dumps(provenance, sort_keys=True),
    }


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ChunkValidationError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _valid_uuid(value: object, label: str) -> str:
    try:
        return str(UUID(_required_text(value, label)))
    except ValueError as error:
        raise ChunkValidationError(f"{label} must be a UUID") from error


def _valid_date(value: object, label: str) -> date:
    try:
        return date.fromisoformat(_required_text(value, label))
    except ValueError as error:
        raise ChunkValidationError(f"{label} must use ISO date format YYYY-MM-DD") from error


def _optional_date(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _valid_date(value, label).isoformat()


def _reject_unredacted_pii(value: str | None, label: str) -> None:
    if value is None:
        return
    for name, pattern in REDACTION_PATTERNS:
        if pattern.search(value):
            raise ChunkValidationError(f"{label} contains unredacted {name}")


def main() -> None:
    """Load a staged corpus with the database selected by DHARA_DATABASE_URL."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    result = asyncio.run(load_into_database(args.chunks, args.receipt))
    print(
        json.dumps(
            {
                "chunk_count": result.chunk_count,
                "dataset_id": result.dataset_id,
                "dataset_version": result.dataset_version,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
