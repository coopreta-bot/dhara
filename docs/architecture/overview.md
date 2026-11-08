# Architecture

Dhara is Module 14 of Coopreta One. It consumes Party, Organization, documents, the ledger, and agri/PACS/FPO records. It does not replace those modules and it does not get built ahead of them.

```
Channels (WhatsApp, Android offline, Web, IVR/USSD, SMS/IVR fallback)
        |
Dhara orchestrator (self-built runtime)
  intent routing, skill dispatch, tool calling, memory
  guardrails: PII filter, Maker/Checker, refusal policy
        |
Skills  <->  RAG engine  <->  model stack  <->  decision intelligence
        |
Data fabric / economic graph (single source of truth)
```

Every box runs on Coopreta-owned or Coopreta-leased infrastructure. A rented GPU is compute. A third-party chat API is not.

## Three model tiers

| Tier | Size | Role |
| --- | --- | --- |
| Edge | 1–3B, GGUF int4 | On-device Android when the village has no link |
| Core | 7–13B | Daily skills, RAG answers, drafts |
| Deep | 30B+ or MoE, later | Multi-step lending or legal reasoning, always Maker/Checker |

Each promoted model has a card in `docs/model-cards/`: base checkpoint, data lineage, Dhara-Bench score, known limits, status.

## RAG

- Store: PostgreSQL 16 + pgvector. Qdrant or Milvus only if scale forces it, still self-hosted.
- Embeddings: a Coopreta-fine-tuned multilingual encoder. Generic embeddings are weak on Anuppur dialect.
- Chunking follows the document type.
- Lending, legal, and compliance answers cite `source_doc_type`, source ref, and date.
- Index partition key is the Party/Organization id.

## Skills and tools

Fourteen skills are registered from `skills/*/manifest.yaml`. Tools are the five MCP servers under `mcp-servers/`. The orchestrator is the only MCP client in the request path.

## Events

Redpanda carries `sos.alerts`, `satellite.ndvi.updates`, `mandi.price.updates`, and `csp.transactions`. Producers publish; the orchestrator, BI, and the RAG indexer subscribe. Ingestion cadence stays separate from model load.

## Channels

Public exposure is limited to channel webhooks behind a WAF and rate limit. GPU nodes, Redpanda, and databases have no public IP.
