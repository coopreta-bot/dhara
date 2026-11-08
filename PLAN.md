# Plan

Dhara-0 and Dhara-1 can start as documents and a RAG proof. Dhara-2 onward waits on the Agriculture, PACS/FPO, Lending, and BI data models. Satellite, SOS, and market skills land after the orchestrator and the event backbone exist. AI does not front-run the platform it reads.

The phase prompts and commands live in [docs/plan/phases.md](docs/plan/phases.md).
Current step: **Phase 0 scaffold is in the tree; Phase 1 has async database
lifecycle wiring, local consent-gated chunk staging, and a self-hosted
pgvector migration/loader, local integration-environment, and remote CI
integration artifacts; the published pgvector job is BLOCKED by the GitHub
account billing lock, and the RAG runtime remains OPEN.**

## Now

1. Keep this repo as the Module 14 tree (sections 3, 3A, and 3B of the blueprint).
2. Pull the legal escalation corpus and vermicompost SOPs into ingestion first, once a DPDP record exists for each.
3. Do not schedule GPU or Redpanda into the current AWS account. Carve out an isolated account or clear the P0 findings first.
4. Choose the open-weight family for the core model and prove RAG plus one skill before any fine-tune.
5. Draft Dhara-Bench v0 from 20–30 real Coopreta documents.
6. Confirm Sentinel Hub or Bhuvan, and eNAM or Agmarknet, in writing before building those connectors.
7. Line up the agronomist/vet relationship before Krishi SOS meets a farmer.

## Spend

Fund Dhara-0/1 with engineering time. Gate the first 7B–13B fine-tune on loan resolution or a dedicated innovation grant. Do not divert vermicompost or fintech working capital into GPU rental. Owned GPUs wait until a rented-GPU cost curve justifies them.

## Team additions

On the Agentic AI pod: MLOps, applied NLP, RAG, streaming, GIS/remote sensing, evaluation, market/demand analysis, and a DPDP/AI-governance role shared with GRC. An on-call agronomist or veterinarian is a domain role, not an engineering headcount, and it is required for Krishi SOS.
