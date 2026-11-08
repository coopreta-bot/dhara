"""Consent-gated, local corpus cleaning and chunking for the RAG index."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from uuid import UUID

DEFAULT_CHUNK_CHARS = 1_000
SCHEMA_VERSION = "1.0"

AADHAAR_PATTERN = re.compile(r"(?<!\d)\d{4}[-\s]\d{4}[-\s]\d{4}(?!\d)")
ACCOUNT_NUMBER_PATTERN = re.compile(
    r"(?i)\b(?:account|a/c)\s*(?:number|no\.?)?\s*[:#-]?\s*\d{6,24}\b"
)
PHONE_NUMBER_PATTERN = re.compile(r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)")
EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
REDACTION_PATTERNS = (
    ("AADHAAR", AADHAAR_PATTERN),
    ("ACCOUNT_NUMBER", ACCOUNT_NUMBER_PATTERN),
    ("PHONE_NUMBER", PHONE_NUMBER_PATTERN),
    ("EMAIL", EMAIL_PATTERN),
)


class IngestionValidationError(ValueError):
    """Raised when a corpus cannot pass the local ingestion gate."""


@dataclass(frozen=True)
class DatasetManifest:
    """Minimum governance metadata required before corpus processing."""

    dataset_id: str
    dataset_version: str
    corpus: str
    tenant_id: str
    consent_record_id: str
    consent_recorded_at: str
    retention_record_id: str
    retention_expires_at: str
    source_kind: str
    source_system: str
    terms_ref: str
    retrieved_at: str | None


def load_manifest(manifest_path: Path) -> DatasetManifest:
    """Load a dataset manifest and require consent, retention, and provenance."""
    payload = _read_json_object(manifest_path, "manifest")

    consent = _required_mapping(payload, "consent", "manifest")
    retention = _required_mapping(payload, "retention", "manifest")
    provenance = _required_mapping(payload, "provenance", "manifest")

    consent_recorded_at = _required_date(consent, "recorded_at", "consent")
    retention_expires_at = _required_date(retention, "expires_at", "retention")
    if date.fromisoformat(retention_expires_at) < date.fromisoformat(consent_recorded_at):
        raise IngestionValidationError(
            "retention.expires_at must not be earlier than consent.recorded_at"
        )

    source_kind = _required_text(provenance.get("kind"), "provenance.kind")
    if source_kind not in {"internal", "public"}:
        raise IngestionValidationError("provenance.kind must be either 'internal' or 'public'")

    retrieved_at: str | None = None
    if source_kind == "public":
        retrieved_at = _required_date(provenance, "retrieved_at", "provenance")

    tenant_id = _required_text(payload.get("tenant_id"), "tenant_id")
    try:
        tenant_id = str(UUID(tenant_id))
    except ValueError as error:
        raise IngestionValidationError("tenant_id must be a UUID") from error

    return DatasetManifest(
        dataset_id=_required_text(payload.get("dataset_id"), "dataset_id"),
        dataset_version=_required_text(payload.get("dataset_version"), "dataset_version"),
        corpus=_required_text(payload.get("corpus"), "corpus"),
        tenant_id=tenant_id,
        consent_record_id=_required_text(consent.get("record_id"), "consent.record_id"),
        consent_recorded_at=consent_recorded_at,
        retention_record_id=_required_text(retention.get("record_id"), "retention.record_id"),
        retention_expires_at=retention_expires_at,
        source_kind=source_kind,
        source_system=_required_text(provenance.get("system"), "provenance.system"),
        terms_ref=_required_text(provenance.get("terms_ref"), "provenance.terms_ref"),
        retrieved_at=retrieved_at,
    )


def ingest_corpus(
    manifest_path: Path,
    input_dir: Path,
    output_dir: Path,
    *,
    chunk_chars: int = DEFAULT_CHUNK_CHARS,
) -> dict[str, object]:
    """Clean JSON documents into chunk JSONL after applying the consent gate."""
    if chunk_chars <= 0:
        raise IngestionValidationError("chunk_chars must be greater than zero")

    manifest = load_manifest(manifest_path)
    documents = _load_documents(input_dir)
    chunks: list[dict[str, object]] = []
    redaction_counts: Counter[str] = Counter()
    document_ids: set[str] = set()

    for document in documents:
        document_id = _required_text(document.get("document_id"), "document.document_id")
        _reject_pii_in_metadata(document_id, "document.document_id")
        if document_id in document_ids:
            raise IngestionValidationError(f"duplicate document.document_id: {document_id}")
        document_ids.add(document_id)
        source_doc_type = _required_text(
            document.get("source_doc_type"),
            f"document {document_id}.source_doc_type",
        )
        _reject_pii_in_metadata(source_doc_type, f"document {document_id}.source_doc_type")
        source_ref = _required_text(
            document.get("source_ref"), f"document {document_id}.source_ref"
        )
        _reject_pii_in_metadata(source_ref, f"document {document_id}.source_ref")
        as_of_date = _optional_date(
            document.get("as_of_date"), f"document {document_id}.as_of_date"
        )
        title = _optional_text(document.get("title"), f"document {document_id}.title")
        content = _required_text(document.get("content"), f"document {document_id}.content")

        if title is not None:
            title, title_redactions = redact_pii(title)
            redaction_counts.update(title_redactions)
        redacted_content, document_redactions = redact_pii(content)
        redaction_counts.update(document_redactions)
        text_chunks = chunk_text(redacted_content, chunk_chars=chunk_chars)
        if not text_chunks:
            raise IngestionValidationError(f"document {document_id}.content has no usable text")

        for chunk_index, chunk in enumerate(text_chunks):
            chunks.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "chunk_id": _chunk_id(manifest, document_id, chunk_index),
                    "dataset_id": manifest.dataset_id,
                    "dataset_version": manifest.dataset_version,
                    "corpus": manifest.corpus,
                    "tenant_id": manifest.tenant_id,
                    "consent_record_id": manifest.consent_record_id,
                    "retention_record_id": manifest.retention_record_id,
                    "source_doc_type": source_doc_type,
                    "source_ref": source_ref,
                    "title": title,
                    "as_of_date": as_of_date,
                    "chunk_index": chunk_index,
                    "content": chunk,
                    "content_sha256": hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
                    "pii_redactions": dict(sorted(document_redactions.items())),
                    "provenance": {
                        "kind": manifest.source_kind,
                        "system": manifest.source_system,
                        "terms_ref": manifest.terms_ref,
                        "retrieved_at": manifest.retrieved_at,
                    },
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = output_dir / "chunks.jsonl"
    receipt_path = output_dir / "ingestion-receipt.json"
    _atomic_write_jsonl(chunks_path, chunks)

    receipt: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": manifest.dataset_id,
        "dataset_version": manifest.dataset_version,
        "corpus": manifest.corpus,
        "tenant_id": manifest.tenant_id,
        "consent_record_id": manifest.consent_record_id,
        "consent_recorded_at": manifest.consent_recorded_at,
        "retention_record_id": manifest.retention_record_id,
        "retention_expires_at": manifest.retention_expires_at,
        "input_document_count": len(documents),
        "chunk_count": len(chunks),
        "pii_redactions": dict(sorted(redaction_counts.items())),
        "outputs": {
            "chunks": str(chunks_path),
            "receipt": str(receipt_path),
        },
    }
    _atomic_write_json(receipt_path, receipt)
    return receipt


def redact_pii(content: str) -> tuple[str, Counter[str]]:
    """Replace regulated identifiers before document text reaches an output file."""
    redactions: Counter[str] = Counter()
    redacted = content
    for name, pattern in REDACTION_PATTERNS:
        redacted, replaced = pattern.subn(f"[REDACTED:{name}]", redacted)
        redactions[name] += replaced
    return redacted, redactions


def chunk_text(content: str, *, chunk_chars: int = DEFAULT_CHUNK_CHARS) -> list[str]:
    """Chunk normalized text at paragraph and sentence boundaries where possible."""
    paragraphs = [
        re.sub(r"\s+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n", content)
        if re.sub(r"\s+", " ", paragraph).strip()
    ]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        for segment in _split_oversized_text(paragraph, chunk_chars):
            candidate = segment if not current else f"{current}\n\n{segment}"
            if len(candidate) <= chunk_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = segment

    if current:
        chunks.append(current)
    return chunks


def _load_documents(input_dir: Path) -> list[dict[str, Any]]:
    if not input_dir.is_dir():
        raise IngestionValidationError(f"input directory does not exist: {input_dir}")

    document_paths = sorted(path for path in input_dir.rglob("*.json") if path.is_file())
    if not document_paths:
        raise IngestionValidationError(f"input directory has no JSON documents: {input_dir}")

    return [_read_json_object(path, "document") for path in document_paths]


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise IngestionValidationError(f"{label} file does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise IngestionValidationError(f"{label} file is not valid JSON: {path}") from error

    if not isinstance(payload, dict):
        raise IngestionValidationError(f"{label} file must contain one JSON object: {path}")
    return payload


def _required_mapping(payload: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise IngestionValidationError(f"{label}.{key} must be an object")
    return value


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IngestionValidationError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _required_date(payload: dict[str, Any], key: str, label: str) -> str:
    value = _required_text(payload.get(key), f"{label}.{key}")
    return _validate_date(value, f"{label}.{key}")


def _optional_date(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _validate_date(_required_text(value, label), label)


def _validate_date(value: str, label: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise IngestionValidationError(f"{label} must use ISO date format YYYY-MM-DD") from error


def _reject_pii_in_metadata(value: str, label: str) -> None:
    for name, pattern in REDACTION_PATTERNS:
        if pattern.search(value):
            raise IngestionValidationError(
                f"{label} contains {name}; store a non-PII reference instead"
            )


def _split_oversized_text(text: str, chunk_chars: int) -> list[str]:
    if len(text) <= chunk_chars:
        return [text]

    sentences = [
        sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()
    ]
    segments: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > chunk_chars:
            if current:
                segments.append(current)
                current = ""
            segments.extend(_split_long_sentence(sentence, chunk_chars))
            continue
        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= chunk_chars:
            current = candidate
        else:
            segments.append(current)
            current = sentence

    if current:
        segments.append(current)
    return segments


def _split_long_sentence(sentence: str, chunk_chars: int) -> list[str]:
    segments: list[str] = []
    current = ""
    for word in sentence.split():
        if len(word) > chunk_chars:
            if current:
                segments.append(current)
                current = ""
            segments.extend(
                word[index : index + chunk_chars] for index in range(0, len(word), chunk_chars)
            )
            continue
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= chunk_chars:
            current = candidate
        else:
            segments.append(current)
            current = word
    if current:
        segments.append(current)
    return segments


def _chunk_id(manifest: DatasetManifest, document_id: str, chunk_index: int) -> str:
    value = ":".join(
        (
            manifest.dataset_id,
            manifest.dataset_version,
            document_id,
            str(chunk_index),
        )
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _atomic_write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    content = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in records
    )
    _atomic_write_text(path, content)


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    _atomic_write_text(
        path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def _atomic_write_text(path: Path, content: str) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    """Run the local pipeline without connecting to a database or remote API."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--chunk-chars", type=int, default=DEFAULT_CHUNK_CHARS)
    args = parser.parse_args()

    receipt = ingest_corpus(
        args.manifest,
        args.input_dir,
        args.output_dir,
        chunk_chars=args.chunk_chars,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
