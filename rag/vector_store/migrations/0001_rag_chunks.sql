-- Initial local pgvector store for consent-cleared RAG chunks.
-- Apply only to a self-hosted Postgres instance inside Coopreta's boundary.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  source_chunk_id TEXT NOT NULL,
  dataset_id TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  corpus TEXT NOT NULL,
  consent_record_id TEXT NOT NULL,
  consent_recorded_at DATE NOT NULL,
  retention_record_id TEXT NOT NULL,
  retention_expires_at DATE NOT NULL,
  source_doc_type TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  title TEXT,
  as_of_date DATE,
  content TEXT NOT NULL,
  content_sha256 TEXT NOT NULL,
  pii_redactions JSONB NOT NULL DEFAULT '{}'::jsonb,
  provenance JSONB NOT NULL,
  embedding VECTOR(1024),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT rag_chunks_retention_after_consent
    CHECK (retention_expires_at >= consent_recorded_at),
  CONSTRAINT rag_chunks_tenant_source_chunk_unique UNIQUE (tenant_id, source_chunk_id)
);

CREATE INDEX IF NOT EXISTS rag_chunks_tenant_id_idx ON rag_chunks (tenant_id);
CREATE INDEX IF NOT EXISTS rag_chunks_retention_expires_at_idx
  ON rag_chunks (retention_expires_at);
CREATE INDEX IF NOT EXISTS rag_chunks_embedding_hnsw_idx
  ON rag_chunks USING hnsw (embedding vector_cosine_ops)
  WHERE embedding IS NOT NULL;
