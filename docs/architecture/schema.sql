-- Module 14 tables. They reference Party/Organization and Document ids from
-- Modules 01-02. They do not recreate those tables.
-- Status: OPEN. This file is the contract. It has not been applied to a database.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE rag_chunks (
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
CREATE INDEX rag_chunks_embedding_hnsw_idx ON rag_chunks
  USING hnsw (embedding vector_cosine_ops) WHERE embedding IS NOT NULL;
CREATE INDEX rag_chunks_tenant_id_idx ON rag_chunks (tenant_id);
CREATE INDEX rag_chunks_retention_expires_at_idx ON rag_chunks (retention_expires_at);

CREATE TABLE model_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_name TEXT NOT NULL,
  version TEXT NOT NULL,
  base_checkpoint TEXT NOT NULL,
  training_data_lineage JSONB NOT NULL,
  dhara_bench_score NUMERIC,
  chatgpt_baseline_score NUMERIC,
  status TEXT NOT NULL,
  published_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE skill_invocations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  skill_name TEXT NOT NULL,
  guardrail_tier TEXT NOT NULL,
  input JSONB NOT NULL,
  retrieved_context JSONB,
  output JSONB,
  model_version TEXT,
  reviewer_id UUID,
  reviewer_decision TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  plot_id UUID,
  category TEXT NOT NULL,
  severity TEXT NOT NULL,
  channel TEXT NOT NULL,
  escalated_to TEXT,
  escalated_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE satellite_ndvi_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plot_id UUID NOT NULL,
  image_date DATE NOT NULL,
  ndvi NUMERIC,
  ndmi NUMERIC,
  source TEXT NOT NULL,
  confidence NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE mandi_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  commodity TEXT NOT NULL,
  mandi_name TEXT NOT NULL,
  price_date DATE NOT NULL,
  min_price NUMERIC,
  max_price NUMERIC,
  modal_price NUMERIC,
  source TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE buyer_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  commodity TEXT NOT NULL,
  buyer_name TEXT NOT NULL,
  contact TEXT,
  match_score NUMERIC,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE maker_checker_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invocation_id UUID NOT NULL REFERENCES skill_invocations(id),
  status TEXT NOT NULL DEFAULT 'pending',
  reviewer_id UUID,
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
