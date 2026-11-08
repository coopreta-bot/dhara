# Governance — Module 14

Dhara uses the Coopreta One release bar. There is no looser standard for AI. Items **00–44** of the platform constitution are the checklist; this file does not restate them and does not invent substitutes. A Dhara release is not complete until those items are evidenced the same way as any other module.

## Status vocabulary

Use only these words:

| Status | Meaning |
| --- | --- |
| PASS | The check was run and the evidence meets the bar. |
| IMPLEMENTED | The artifact exists in the tree. Existence is not production proof. |
| LIVE VERIFIED | An independent check, outside the author's say-so, confirmed the running behavior. |
| CONDITIONALLY VERIFIED | Verified only inside a stated limit (environment, tenant, skill, or data slice). |
| OPEN | Not done, or done only as a scaffold. |
| BLOCKED | Cannot proceed until a named dependency is cleared. |
| HUMAN REVIEW REQUIRED | A person must approve before the output is sent, filed, or executed. |
| SECURITY GATE BLOCKED | A security control failed or is missing. Do not deploy. |

Rules:

- No capability is marked PASS, LIVE VERIFIED, or CONDITIONALLY VERIFIED without evidence linked next to the claim.
- Cursor, Devin, or a model saying a phase is done is not evidence.
- A model that fails Dhara-Bench is OPEN or BLOCKED, never "almost ready."
- Financial, legal, and regulatory skill output is HUMAN REVIEW REQUIRED and must not auto-execute.
- Krishi SOS never replaces a human agronomist or veterinarian. Above the severity threshold, escalation is mandatory.

## Hard blockers

| Blocker | Status | What it stops |
| --- | --- | --- |
| AWS foundation P0 (default VPC, no private subnet split, prod/staging co-located, GuardDuty / Security Hub / Config off, admin role with AdministratorAccess) | SECURITY GATE BLOCKED | GPU, Kafka/Redpanda, and database provisioning inside that account |
| Agriculture / PACS / FPO / Lending / BI data models not yet the source of truth | BLOCKED | Dhara-2 training and any skill that needs those canonical records |
| On-call agronomist/vet relationship not in place | BLOCKED | Krishi SOS against a real farmer |
| Satellite and mandi access terms not confirmed in writing | OPEN | Building those connectors past a spike |

Until the AWS item is cleared, ML work stays on documents, local scaffolds, or a deliberately isolated account carved out for ML and streaming.

## Sovereignty rules

- No third-party inference API in the request path.
- Rented GPU hours are allowed. Weights and training data stay under Coopreta's control.
- Public government data (scheme texts, Sentinel-2 / Bhuvan, eNAM / Agmarknet) is allowed. A paid model API wrapped around that data is not.
- PII is scrubbed or tokenized before a training run. That gate is automated once the pipeline exists; it is not a manual reminder.
- Every dataset is versioned and tagged with a consent and retention record before it trains a model.
- Every inference that ships is logged: input, retrieved context, output, model version, reviewer decision.

## Capability register

| Capability | Status | Evidence |
| --- | --- | --- |
| Repository folder scaffold and documents | IMPLEMENTED | This tree. Folders, manifests, and docs exist. No product service is deployed; local MCP contract servers are available. |
| Python lint/test config | IMPLEMENTED | `pyproject.toml`, `.pre-commit-config.yaml`. Hooks are not installed until a developer runs `pre-commit install`. |
| Fourteen skill manifests | IMPLEMENTED | `skills/*/manifest.yaml`. No skill code. |
| Five MCP stdio contract servers | IMPLEMENTED | `mcp-servers/*/manifest.yaml` and stdio MCP entry points. Tools return `OPEN` development contracts. |
| Five MCP business integrations and production deployment | OPEN | No backend adapters or private-network production deployment are implemented. |
| RAG service | OPEN | Async database lifecycle wiring and `GET /health` exist in `rag/`. Local consent-gated PII-scrubbed chunk staging, a pgvector migration, a receipt-validating chunk loader, Compose configuration, an opt-in integration test, and a generated-data-only GitHub Actions workflow exist in `rag/`, `infra/`, `tests/`, and `.github/`; Docker was unavailable on the development host. The published workflow was triggered for commit `23b0714614fe66e801637d74d71909bf4bd0a68c` but could not start because the GitHub account is locked by a billing issue ([run #1](https://github.com/coopreta-bot/dhara/actions/runs/42492866174)). No database has been provisioned or migrated, and embeddings, retrieval, and `POST /query` are not built. |
| Dhara-Bench v0 | OPEN | Held-out set not collected. |
| Orchestrator and Maker/Checker queue | OPEN | Not built. |
| Redpanda dev cluster and four topics | OPEN | Definitions are documents only. |
| Satellite and mandi ingestion | OPEN | Access terms not confirmed. |
| Edge GGUF model and Android path | OPEN | Not built. |
| Isolated ML/streaming account | SECURITY GATE BLOCKED | Depends on the AWS P0 hold. |
