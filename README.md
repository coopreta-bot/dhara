# Coopreta Dhara

Coopreta's self-hosted, sovereign agentic AI system. This repository is **Module 14 (AI/ML/RAG/Agents/Decision Intelligence)** of Coopreta One, built by the Agentic AI / Experience / Offline UX execution pod.

Dhara owns, hosts, fine-tunes, and runs every model on infrastructure Coopreta controls. The request path does not call OpenAI, Anthropic, Google, or any other third-party inference API. Open-weight research checkpoints (Llama, Mistral, or Qwen class) may be vendored as starting weights. That is model sovereignty: Coopreta's data and weights stay inside Coopreta's boundary.

The "10x" claim is narrower than general intelligence. Dhara is meant to be better than a general chatbot on Coopreta's own surface: SOPs, KCC/PACS forms, CGSS/CGTMSE appraisal language, product specs, procurement terms, subsidy schemes, Anuppur/Kotma vernacular Hindi, and Coopreta's escalation-letter style. The yardstick is **Dhara-Bench**, a held-out set of real Coopreta documents, not a public leaderboard.

## Status

Phase 0 is a document and folder scaffold. No capability in this tree is LIVE VERIFIED. Status words are defined in [GOVERNANCE.md](GOVERNANCE.md). The build order is in [PLAN.md](PLAN.md).

GPU, Kafka, and database workloads stay unscheduled until the AWS foundation P0 hold is cleared or an isolated ML/streaming account boundary exists. See the source draft: [Coopreta Dhara — Sovereign Agentic AI Platform.md](Coopreta%20Dhara%20%E2%80%94%20Sovereign%20Agentic%20AI%20Platform.md).

## Layout

| Path | Role |
| --- | --- |
| `docs/` | Architecture, model cards, data governance, ADRs, plan, setup |
| `infra/` | Isolated network, clusters, monitoring, model CI |
| `data/` | Ingestion, pipelines, annotation, dataset versions |
| `models/` | Base weights, continued pretraining, SFT, DPO, distillation, embeddings, eval, registry |
| `rag/` | Chunking, pgvector, retriever, reranker, citations |
| `orchestrator/` | Router, tool calling, memory, guardrails, skill registry |
| `skills/` | Fourteen Dhara Skills, each with a manifest |
| `channels/` | WhatsApp, Android offline, web, IVR/USSD, SMS/IVR fallback |
| `i18n/` | Language and regulatory packs |
| `security/` | PII redaction, access control, audit trail |
| `streaming/` | Redpanda topics, producers, consumers |
| `mcp-servers/` | Five internal MCP servers |
| `tests/` | Unit, integration, eval, red team |
| `scripts/` | Bootstrap, eval, deploy (stubs that exit until implemented) |

## Tooling

Python 3.11. Dev tools are declared in `pyproject.toml`: Black, Ruff, pytest, pre-commit. Install and hook setup are in [docs/setup/README.md](docs/setup/README.md).

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```
