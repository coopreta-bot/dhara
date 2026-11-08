from __future__ import annotations

import json

import pytest

from rag.ingestion.pipeline import IngestionValidationError, ingest_corpus

TENANT_ID = "00000000-0000-0000-0000-000000000001"


def write_manifest(path, *, consent_record_id: str = "dpdp-consent-001") -> None:
    path.write_text(
        json.dumps(
            {
                "dataset_id": "vermicompost-ops",
                "dataset_version": "2026-11-08",
                "corpus": "vermicompost_ops",
                "tenant_id": TENANT_ID,
                "consent": {
                    "record_id": consent_record_id,
                    "recorded_at": "2026-11-01",
                },
                "retention": {
                    "record_id": "retention-001",
                    "expires_at": "2027-11-01",
                },
                "provenance": {
                    "kind": "internal",
                    "system": "coopreta-document-store",
                    "terms_ref": "records-policy-2026",
                },
            }
        ),
        encoding="utf-8",
    )


def test_ingest_corpus_writes_consent_linked_pii_redacted_chunks(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    write_manifest(manifest_path)
    (input_dir / "vermicompost-sop.json").write_text(
        json.dumps(
            {
                "document_id": "vermicompost-sop-001",
                "source_doc_type": "vermicompost_sop",
                "source_ref": "document-store/vermicompost-sop-001",
                "title": "Vermicompost bed SOP",
                "as_of_date": "2026-10-15",
                "content": (
                    "Prepare a shaded bed with adequate drainage. "
                    "Call +91 9876543210 before delivery. "
                    "Aadhaar 1234 5678 9012 must never enter the index. "
                    "Account no: 12345678901234 must never enter the index. "
                    "Email farmer@example.com must never enter the index."
                ),
            }
        ),
        encoding="utf-8",
    )

    receipt = ingest_corpus(
        manifest_path,
        input_dir,
        output_dir,
        chunk_chars=90,
    )

    chunks = [
        json.loads(line)
        for line in (output_dir / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    combined_content = "\n".join(chunk["content"] for chunk in chunks)

    assert receipt["input_document_count"] == 1
    assert receipt["chunk_count"] == len(chunks)
    assert receipt["pii_redactions"] == {
        "AADHAAR": 1,
        "ACCOUNT_NUMBER": 1,
        "EMAIL": 1,
        "PHONE_NUMBER": 1,
    }
    assert "9876543210" not in combined_content
    assert "1234 5678 9012" not in combined_content
    assert "12345678901234" not in combined_content
    assert "farmer@example.com" not in combined_content
    assert "[REDACTED:PHONE_NUMBER]" in combined_content
    assert "[REDACTED:AADHAAR]" in combined_content
    assert all(len(chunk["content"]) <= 90 for chunk in chunks)
    assert all(chunk["tenant_id"] == TENANT_ID for chunk in chunks)
    assert all(chunk["consent_record_id"] == "dpdp-consent-001" for chunk in chunks)
    assert all(chunk["retention_record_id"] == "retention-001" for chunk in chunks)
    assert all(chunk["source_doc_type"] == "vermicompost_sop" for chunk in chunks)

    saved_receipt = json.loads((output_dir / "ingestion-receipt.json").read_text(encoding="utf-8"))
    assert saved_receipt == receipt


def test_ingest_corpus_rejects_a_manifest_without_a_consent_record(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    input_dir.mkdir()
    write_manifest(manifest_path, consent_record_id="")

    with pytest.raises(IngestionValidationError, match="consent.record_id"):
        ingest_corpus(manifest_path, input_dir, tmp_path / "output")


def test_ingest_corpus_rejects_duplicate_document_ids(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    input_dir.mkdir()
    write_manifest(manifest_path)
    for filename in ("first.json", "second.json"):
        (input_dir / filename).write_text(
            json.dumps(
                {
                    "document_id": "duplicate-document",
                    "source_doc_type": "vermicompost_sop",
                    "source_ref": f"document-store/{filename}",
                    "content": "Use only mature compost.",
                }
            ),
            encoding="utf-8",
        )

    with pytest.raises(IngestionValidationError, match="duplicate document.document_id"):
        ingest_corpus(manifest_path, input_dir, tmp_path / "output")


def test_ingest_corpus_rejects_pii_in_a_source_reference(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    input_dir.mkdir()
    write_manifest(manifest_path)
    (input_dir / "document.json").write_text(
        json.dumps(
            {
                "document_id": "sop-001",
                "source_doc_type": "vermicompost_sop",
                "source_ref": "farmer/9876543210/document",
                "content": "Use only mature compost.",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(IngestionValidationError, match="source_ref contains PHONE_NUMBER"):
        ingest_corpus(manifest_path, input_dir, tmp_path / "output")


def test_ingest_corpus_scrubs_pii_from_a_citation_title(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    input_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    write_manifest(manifest_path)
    (input_dir / "document.json").write_text(
        json.dumps(
            {
                "document_id": "sop-001",
                "source_doc_type": "vermicompost_sop",
                "source_ref": "document-store/sop-001",
                "title": "Contact farmer@example.com",
                "content": "Use only mature compost.",
            }
        ),
        encoding="utf-8",
    )

    receipt = ingest_corpus(manifest_path, input_dir, output_dir)
    chunk = json.loads((output_dir / "chunks.jsonl").read_text(encoding="utf-8"))

    assert chunk["title"] == "Contact [REDACTED:EMAIL]"
    assert receipt["pii_redactions"] == {
        "AADHAAR": 0,
        "ACCOUNT_NUMBER": 0,
        "EMAIL": 1,
        "PHONE_NUMBER": 0,
    }
