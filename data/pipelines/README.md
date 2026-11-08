# pipelines

Cleaning, PII scrubbing, and document-aware chunking for local RAG staging.

## Consent gate

`rag/ingestion/pipeline.py` is an IMPLEMENTED local pipeline that accepts only
a JSON dataset manifest with a consent record, a retention record, provenance,
and a tenant UUID. It rejects missing records and PII-bearing source
references, redacts Aadhaar values, labelled account numbers, Indian phone
numbers, and email addresses in document text and citation titles, then writes
chunk JSONL and an ingestion receipt. It does not call a third-party API,
create embeddings, load Postgres, or make the corpus eligible for training.

Each input document is one JSON object:

```json
{
  "document_id": "vermicompost-sop-001",
  "source_doc_type": "vermicompost_sop",
  "source_ref": "document-store/vermicompost-sop-001",
  "title": "Optional citation title",
  "as_of_date": "2026-10-15",
  "content": "Document text"
}
```

The manifest requires `dataset_id`, `dataset_version`, `corpus`, `tenant_id`,
`consent.record_id`, `consent.recorded_at`, `retention.record_id`,
`retention.expires_at`, and `provenance`. Public provenance additionally
requires `provenance.retrieved_at`. Store neither real documents nor manifests
with sensitive references in Git. Each input directory is an authoritative
snapshot of one dataset version: document IDs must be unique.

```powershell
python -m rag.ingestion.pipeline `
  --manifest .\path\to\manifest.json `
  --input-dir .\path\to\documents `
  --output-dir .\data\pipelines\output\vermicompost-ops
```

`data/pipelines/output/` is ignored by Git. The RAG index, embeddings, and
database loading remain OPEN. After a self-hosted pgvector migration is
applied, use `rag.vector_store.loader.load_staged_chunks` with both generated
files; it refuses expired retention records and unredacted PII.
