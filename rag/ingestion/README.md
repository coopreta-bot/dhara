# ingestion

Builds consent-gated, PII-scrubbed cleaned chunks before any vector-store load.

`pipeline.py` is IMPLEMENTED for local JSON documents. It requires dataset
consent, retention, tenant, and provenance metadata; produces citation-ready
JSONL in `data/pipelines/output/`; and does not make a database connection.
See [data/pipelines/README.md](../../data/pipelines/README.md) for the input
contract and command.

`rag.vector_store.loader` can then validate the JSONL plus its receipt and
upsert it into a self-hosted pgvector database. Applying the migration and
loading a real corpus have not been independently verified. Embedding,
retrieval, and reindexing remain OPEN.
