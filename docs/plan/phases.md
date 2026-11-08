# Phases

Each phase ends by updating [GOVERNANCE.md](../../GOVERNANCE.md) with the restricted vocabulary. A phase is not LIVE VERIFIED because Cursor produced the code.

## Phase 0 — Repo and governance scaffold

Status: IMPLEMENTED for folders, documents, manifests, and Python config. OPEN for hook installation on a developer machine and for any service.

Done in this tree:

- Top-level folders from the blueprint, including streaming and `mcp-servers/`
- `README.md`, `GOVERNANCE.md`, `PLAN.md`
- A README in each folder
- `pyproject.toml` and `.pre-commit-config.yaml` (Black, Ruff, pytest)

Still open:

```bash
python -m venv .venv
pip install -e ".[dev]"
pre-commit install
```

Do not commit secrets. Do not mark Phase 0 LIVE VERIFIED until someone other than the author confirms the tree.

## Phase 1 — Ingestion and RAG MVP

Status: OPEN. Async SQLAlchemy engine/session lifecycle wiring and a database
readiness endpoint are implemented in `rag/database.py` and `rag/app.py`.
`rag/ingestion/pipeline.py` locally validates consent/retention/provenance
metadata, scrubs specified PII, and writes cleaned chunk JSONL.
`rag/vector_store/migrations/0001_rag_chunks.sql` and
`rag/vector_store/loader.py` define a consent-validated pgvector schema and
atomic local snapshot loader. These artifacts do not provision a database,
establish DPDP approval, create embeddings, or implement `POST /query`.
`infra/docker-compose.pgvector.yml` and
`tests/integration/test_pgvector_stack.py` define a local integration
environment and opt-in verification path; Docker is not installed on the
current host, so that path remains unrun.
`.github/workflows/pgvector-integration.yml` provides a remote,
generated-data-only integration path that does not require Docker Desktop.

Build connectors for `legal_escalation_corpus`, `vermicompost_ops`, and `government_schemes`. Write cleaned chunks to `data/pipelines/output/`. Add a self-hosted Postgres + pgvector store, a self-hosted multilingual embedding model, a retriever, and `POST /query` that cites `doc_type` and date.

```bash
docker compose -f infra/docker-compose.pgvector.yml up -d
uvicorn rag.app:app --reload --port 8000
```

Those files do not exist yet. Do not invent a compose file that points at a third-party embedding API.

## Phase 2 — Fine-tune and Dhara-Bench

Status: BLOCKED on a real holdout set and on an explicit spend decision. The pipeline design is: LoRA via transformers + peft, JSONL from `data/annotation/sft_dataset.jsonl`, config at `models/sft/configs/`, harness at `models/eval/dhara_bench.py`, card written to `docs/model-cards/`.

## Phase 3 — Orchestrator, 14 skills, Redpanda

Status: OPEN. Skill folders and manifests already exist. Shared interface: `name`, `input_schema`, `guardrail_tier`, `run(context)`. Maker/Checker middleware queues anything tagged `human_review`. Topics: `sos.alerts`, `satellite.ndvi.updates`, `mandi.price.updates`, `csp.transactions`.

## Phase 4 — Satellite, edge model, DPO

Status: OPEN, and BLOCKED for real farmers until access terms and the agronomist/vet relationship exist. NDVI/NDMI advisories cite imagery date and confidence. DPO lives in `models/preference/`. GGUF int4 ships through `channels/android_offline/`.

## Phase 5 — Market intelligence and tenant isolation

Status: OPEN. Daily public prices into `mandi.price.updates`. Buyer match uses Coopreta CRM. RAG chunks gain a tenant partition. Binding trades stay in Maker/Checker.

## Phase 6 — Another geography

Status: OPEN. Copy `i18n/_template/` to `i18n/<geo-code>`. Add that country's credit-guarantee scheme and data-protection law as data and pack config. Skill code stays unchanged.
