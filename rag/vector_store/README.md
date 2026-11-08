# vector store

Self-hosted pgvector storage. The tenant key is Party/Organization id.

`migrations/0001_rag_chunks.sql` and `migrate.py` are IMPLEMENTED. The
migration enables `vector` and `pgcrypto`, creates a tenant-partitioned
`rag_chunks` table, records consent and retention metadata with every chunk,
and creates a partial HNSW index only for rows that have embeddings.

`loader.py` is IMPLEMENTED. It accepts only the `chunks.jsonl` and
`ingestion-receipt.json` emitted by `rag.ingestion.pipeline`, verifies their
shared dataset metadata and content hashes, rejects expired retention records
or remaining PII, and upserts the chunks atomically. A changed chunk clears its
embedding so a future local embedding job must recreate it. A load treats the
staged JSONL as the authoritative snapshot for its tenant, dataset ID, and
dataset version, deleting rows absent from that snapshot.

No migration runs during FastAPI startup. Set `DHARA_DATABASE_URL` to a
self-hosted `postgresql+asyncpg://` URL and apply it deliberately:

```powershell
python -m rag.vector_store.migrate
python -m rag.vector_store.loader `
  --chunks .\data\pipelines\output\vermicompost-ops\chunks.jsonl `
  --receipt .\data\pipelines\output\vermicompost-ops\ingestion-receipt.json
```

The embedding job, retrieval, and database deployment remain OPEN.
