# Coopreta Dhara — Sovereign Agentic AI Platform

*Module 14 (AI/ML/RAG/Agents/Decision Intelligence) — Coopreta One Master Engineering Plan*

*Status vocabulary in this document follows the existing Coopreta One standard: PASS / IMPLEMENTED / LIVE VERIFIED / CONDITIONALLY VERIFIED / OPEN / BLOCKED / HUMAN REVIEW REQUIRED / SECURITY GATE BLOCKED.*

## 0. Reality Check — Read This Before Anything Else

Two requirements need an engineering-honest translation before any plan built on them is credible, not fiction:

**"Khud ka model banana, koi external API/model use nahi karna"** — Literally training a frontier transformer from random weights that beats GPT-4-class models needs on the order of tens of thousands of GPUs, trillions of tokens of curated data, and hundreds of millions of dollars. No startup at Coopreta's stage does this — not Indian unicorns, not Series-C AI labs. What **is** realistic, and what this plan builds, is **model sovereignty**: Coopreta owns, hosts, fine-tunes, and runs every model on infrastructure it controls, with zero runtime calls to OpenAI/Anthropic/Google/any third-party inference API. Starting weights come from permissively-licensed open-weight research (Llama/Mistral/Qwen-class families) — this is exactly how every serious "build your own LLM" program in the world works, including ones run by banks and governments. Nobody pays a per-token API bill, nobody outside Coopreta sees the data, the model physically runs on Coopreta's own servers. That is the honest meaning of "apna model."

**"ChatGPT se 10X better"** — Generic ChatGPT will always out-perform Dhara on general knowledge; it was trained on the whole internet with vastly more compute. Dhara can be genuinely, provably better on a narrower, deeper surface: Coopreta's own SOPs, KCC/PACS documentation formats, CGSS/CGTMSE appraisal language, Dr. Bacto's product specs, Kalmegh procurement terms, vermicompost subsidy schemes, Anuppur/Kotma vernacular Hindi, and Coopreta's own escalation-letter style — because ChatGPT has never seen any of that and Dhara is trained and grounded on nothing else. That is the "10x" this plan commits to: **10x better at being Coopreta's own brain**, not 10x better at general intelligence. This framing is also the stronger, more defensible pitch to DPIIT/investors/RBI than an unfalsifiable general-benchmark claim.

Everything below is built on these two honest premises.

## 1. Where Dhara Sits in Coopreta One

Dhara is **not a parallel project** — it is the concrete build-out of **Module 14 (AI/ML/RAG/Agents/Decision Intelligence)** in the existing 16-module Coopreta One architecture, executed by the **Agentic AI/Experience/Offline UX** Execution Pod, under the same Devin-driven 45-point verification spine already governing earlier phases.

Consequences of this placement:

- Dhara inherits the stated phase order — Agriculture → PACS/FPO → Commerce → Lending → BI → AI → Satellite → Global. Module 14 build should not front-run the Agriculture/PACS/FPO/Lending/BI data models, because Dhara's RAG and skills are consumers of exactly that canonical data (Party/Organization, Economic Graph, Master Data). Building the brain ahead of the body produces nothing usable.
- Dhara inherits the full governance baseline (PCI DSS, ISO 27001/27701, SOC 2, GDPR, India DPDP, OWASP ASVS, NIST SSDF, Zero Trust, RBAC+ABAC, Maker/Checker, immutable audit trail) — an AI module touching lending and farmer data is one of the highest-risk modules in the platform, not an exception to the baseline.
- Dhara must pass the same 45-point checklist (00–44) on every release, using the same restricted status vocabulary. No "production ready" or "certified" claims without independently verified evidence — doubly important for AI, since model outputs are probabilistic and easy to oversell.
- **Blocking prerequisite**: the Amazon Q audit already found P0 gaps in the AWS foundation (default VPC, no private subnet segmentation, prod/staging co-located on one EC2 instance, GuardDuty/Security Hub/Config disabled, an admin role with AdministratorAccess). GPU training/inference workloads must not be scheduled onto that foundation. Module 14 infra work should start only after the AWS foundation HOLD is cleared, or on a deliberately isolated/segmented account boundary carved out specifically for ML workloads in the meantime.

## 2. Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│ CHANNELS: WhatsApp Bot · Android (offline-first) · Web · IVR/USSD │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
┌────────────────────────────── ▼ ──────────────────────────────────┐
│ DHARA ORCHESTRATOR (self-built agent runtime, no external agent API)│
│  - intent routing · skill dispatch · tool-calling · memory          │
│  - guardrails: PII filter, Maker/Checker gate, refusal policy       │
└───┬───────────────┬───────────────┬───────────────┬───────────────┘
    │               │               │               │
┌───▼───┐      ┌────▼────┐    ┌─────▼─────┐   ┌──────▼──────┐
│ SKILLS │      │  RAG     │    │  MODEL     │   │  DECISION    │
│ LAYER  │◄────►│  ENGINE  │◄──►│  STACK     │   │  INTELLIGENCE│
│(sec.7) │      │ (sec.6)  │    │  (sec.5)   │   │  / BI (Mod.13)│
└────────┘      └──────────┘    └────────────┘   └──────────────┘
    │               │               │
┌───▼───────────────▼───────────────▼────────────────────────────────┐
│ DATA FABRIC / ECONOMIC GRAPH (Modules 01-03, 13) — Party, Org,      │
│ Documents, Ledger, Agri/PACS/FPO records — single source of truth  │
└──────────────────────────────────────────────────────────────────┘
```

Every box above runs on Coopreta-owned/leased infrastructure (own VPC, own GPU nodes or a dedicated isolated cloud account) — never a third-party inference API in the request path.

## 3. Repo Structure

Monorepo, aligned to the existing 16-module numbering so Devin's module boundaries stay consistent:

```
coopreta-dhara/
├── README.md
├── GOVERNANCE.md                     # 45-point checklist + status vocabulary for this module
├── docs/
│   ├── architecture/
│   ├── model-cards/                  # every model: data lineage, eval, limitations
│   ├── data-governance/              # DPDP/consent/retention policy per corpus
│   └── adr/                          # architecture decision records
├── infra/
│   ├── terraform/                    # isolated VPC, GPU node groups, private subnets
│   ├── k8s/                          # inference + training clusters, autoscaling
│   ├── monitoring/                   # drift, latency, cost, GuardDuty/Security Hub hooks
│   └── ci-cd/                        # model CI: eval-gate before any promotion
├── data/
│   ├── ingestion/                    # connectors to Coopreta's own systems only
│   │   ├── pacs_kcc/
│   │   ├── fintech_aeps_dmt_bbps/
│   │   ├── vermicompost_ops/
│   │   ├── legal_escalation_corpus/
│   │   ├── social_media_corpus/      # Khet Se Baat archive
│   │   └── government_schemes/       # NABARD/RKVY/NMSA/CGSS/CGTMSE texts
│   ├── pipelines/                    # cleaning, dedup, PII scrub, chunking
│   ├── annotation/                   # labeling tools + guidelines (Hindi/vernacular)
│   └── versioning/                   # DVC/lakeFS — every dataset version pinned
├── models/
│   ├── base/                         # open-weight base checkpoints (vendored, self-hosted)
│   ├── pretrain-continued/           # domain-adaptive continued pretraining scripts
│   ├── sft/                          # supervised fine-tuning (instruction data)
│   ├── preference/                   # DPO/RLHF on Coopreta-specific preference pairs
│   ├── distillation/                 # small edge models distilled from the fine-tuned model
│   ├── embeddings/                   # self-hosted embedding model (training + eval)
│   ├── eval/                         # Dhara-Bench: Coopreta-specific eval harness
│   └── registry/                     # model registry, versioning, rollback
├── rag/
│   ├── ingestion/
│   ├── chunking/
│   ├── vector_store/                 # self-hosted (pgvector/Qdrant/Milvus — no managed 3P API)
│   ├── retriever/
│   ├── reranker/
│   └── grounding/                    # citation + confidence scoring
├── orchestrator/
│   ├── router/
│   ├── tool_calling/
│   ├── memory/
│   ├── guardrails/                   # PII filter, Maker/Checker, refusal policy, audit log
│   └── skills_registry/
├── skills/                           # one folder per Dhara Skill — see section 7
├── channels/
│   ├── whatsapp/
│   ├── android_offline/
│   ├── web_widget/
│   └── ivr_ussd/
├── i18n/                             # language packs — see section 11
│   ├── hi-MP-anuppur/                # vernacular Hindi dialect pack
│   ├── hi-IN/
│   ├── en-IN/
│   └── _template/                    # new language/geography pack scaffold
├── security/
│   ├── pii_redaction/
│   ├── model_access_control/         # RBAC+ABAC on model + data access
│   └── audit_trail/                  # immutable log, ties into platform-wide audit
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── eval/                         # automated Dhara-Bench runs, gate for promotion
│   └── red_team/                     # adversarial/jailbreak/hallucination tests
└── scripts/
    ├── bootstrap_dev_env.sh
    ├── run_eval_suite.sh
    └── deploy.sh
```

## 4. Data Strategy & Sovereignty

Dhara's entire intelligence advantage comes from data Coopreta already owns and nobody else has:

| Corpus | Source | Use |
| --- | --- | --- |
| PACS/KCC/UniTERP documentation | Ashish's own PACS digitization work | SFT + RAG for loan documentation skill |
| Fintech transaction patterns (AEPS/DMT/BBPS/CSP) | Coopreta's own CSP operations | Fintech Sahayak skill, fraud/BI signals |
| Legal escalation corpus | RTI applications, RBI/DPIIT/Collector letters, Central Bank of India CGSS/CGTMSE case, High Court submission | Grievance & legal drafting skill |
| Vermicompost SOPs & subsidy filings | NABARD/RKVY/NMSA documentation, production plans | Vermicompost ops skill |
| Social content archive | Khet Se Baat scripts, Instagram/Facebook content | Content generation skill, tone model |
| Government scheme texts | Public DPIIT/NABARD/RBI scheme documents | RAG knowledge base (public, curated) |
| Agri-input & bio-fertiliser specs | Dr. Bacto's product line, Kalmegh procurement | Krishi Salah skill |

Rules:

- No data leaves Coopreta's infrastructure for training or inference — everything stays inside the same VPC/account boundary the governance baseline already mandates.
- Every dataset is versioned (DVC/lakeFS) and tagged with a DPDP-compliant consent/retention record before it touches a model.
- PII (farmer Aadhaar/account numbers, phone numbers) is scrubbed or tokenized before any training run — enforced as an automated pipeline gate, not a manual step.
- Vernacular Hindi (Anuppur/Kotma dialect) gets its own annotation guideline and a held-out eval set — a genuine moat no general model matches.

## 5. Model Strategy — Three-Tier Stack, Fully Self-Hosted

| Tier | Purpose | Approach |
| --- | --- | --- |
| Edge/Offline (1-3B params) | Runs on low-end Android in low/no-connectivity villages | Distilled from Tier 2, quantized (GGUF/int4), on-device |
| Core Domain Model (7-13B params) | Day-to-day Dhara brain — skills, RAG answering, drafting | Open-weight base → continued pretraining on Coopreta corpus → SFT on Coopreta instruction data → DPO on Coopreta preference pairs |
| Deep Reasoning (30B+/MoE, later phase) | Complex multi-step lending/legal reasoning, always Maker/Checker-gated | Same pipeline, larger base, used sparingly given compute cost |

Every tier: self-hosted weights, zero runtime dependency on a third-party API, versioned in the model registry, carries a model card (training data lineage, known limitations, eval scores).

**Dhara-Bench** (`models/eval/`) is the only benchmark that matters for the "10x" claim: built from held-out Coopreta documents — can Dhara draft a CGTMSE appraisal escalation as well as Ashish would, answer a Kalmegh procurement question correctly, produce a correct vermicompost subsidy filing clause. ChatGPT runs on the same held-out set as the baseline — that comparison is the real, defensible "10x" number, published in the model card.

## 6. RAG Architecture

- **Vector store**: self-hosted pgvector (fits the existing Postgres-centric Data Fabric) or Qdrant/Milvus at scale — never a managed third-party vector API.
- **Embeddings**: own fine-tuned embedding model (small, distilled multilingual encoder), trained on Coopreta's Hindi/English mixed corpus — generic embedding models underperform badly on Anuppur-dialect text.
- **Chunking**: document-aware — a KCC form chunks differently than a social media script.
- **Grounding & citation**: every answer touching lending, legal, or compliance content must cite the source document/clause — both an accuracy control and an audit-trail requirement under the governance baseline.
- **Multi-tenant isolation**: RAG indices partitioned per the existing Party/Organization model — critical once Dhara serves other FPOs/PACS beyond Coopreta (global expansion, section 11).

## 7. Agentic Skills Layer — "Dhara Skills"

Each skill is a self-contained module with its own tools, data scope, and guardrail level. The original 8 are extended here with 6 more covering emergency response, satellite intelligence, and market/commerce needs:

1. **Krishi Salah** (Agri Advisory) — crop/input guidance, Dr. Bacto's & Kalmegh product Q&A, grounded in agronomy RAG. *Guardrail: informational only; no autonomous input-mix prescriptions without a human agronomist sign-off above a stated risk threshold.*
2. **Fintech Sahayak** (CSP Assistant) — AEPS/DMT/BBPS/CSP transaction help, dispute triage. *Guardrail: HUMAN REVIEW REQUIRED for anything touching money movement.*
3. **PACS/KCC Documentation** — drafts and checks KCC loan paperwork using UniTERP-derived templates. *Guardrail: Maker/Checker before submission.*
4. **Grievance & Escalation Drafting** — RTI, RBI/DPIIT/Collector letters, High Court submission drafts, grounded in the actual case corpus (Central Bank of India CGSS/CGTMSE matter, SBI representation). *Guardrail: human sign-off mandatory before any filing.*
5. **Vermicompost Ops & Subsidy** — bed-scaling and OPEX/CAPEX tracking, NABARD/RKVY/NMSA subsidy filing assistance.
6. **Khet Se Baat Content Engine** — Hinglish farmer-facing social content, CMD persona tone, the 365-day engagement question bank.
7. **Legal & Compliance Drafting** — contracts, policy documents, DPIIT/MSME filings.
8. **BI / Decision Support** — natural-language interface over Module 13's Economic Graph/BI layer.
9. **Krishi SOS — Agricultural Emergency Response** — multi-channel SOS (app button + WhatsApp + IVR/SMS fallback for feature phones) for crop disease outbreaks, pest attacks, extreme-weather warnings, and livestock health emergencies; triages severity and escalates to a human agronomist/vet/extension officer. *Guardrail: never withholds a human handoff — above a defined severity, escalation is automatic, not model-judged.*
10. **Satellite Crop Intelligence** — ingests open satellite imagery (Sentinel-2/ISRO Bhuvan — public data, not a paid third-party AI API) for Coopreta's registered plots; computes NDVI/soil-moisture trends for crop-stress and drought/flood early-warning, feeding Krishi Salah and Krishi SOS. Aligns with Coopreta One's own "Satellite" platform phase. *Guardrail: advisory only, always cites the imagery date and confidence.*
11. **Mandi Price & Buyer Connect** — ingests public mandi price bulletins (eNAM/Agmarknet — public government data, not a model dependency) and matches Coopreta's sellers (vermicompost, Kalmegh, Dr. Bacto's line) to buyer leads from Coopreta's own CRM. *Guardrail: Maker/Checker before any binding transaction; every price cited with its source and as-of date.*
12. **Market Research & Demand Signal Engine** — combines Coopreta's own sales/transaction history with public agri-statistics to project local demand for bio-inputs, vermicompost, and crop inputs; feeds BI/Decision Support (#8).
13. **Customer Finder / Lead Matching** — ranks prospective CSP, vermicompost, and bio-input customers from Coopreta's own CRM and village outreach data, prioritising field-agent visits.
14. **Community & Social Layer** — a moderated farmer-to-farmer Q&A board (distinct from #6's outward marketing content); Dhara fact-checks answers before they reach other farmers and feeds good Q&A back into the RAG corpus.

New skills plug into `skills/` with a manifest (name, data scope, tools, guardrail tier) and register with the orchestrator — the extensibility point for future skills without touching the core model or RAG engine.

## 8. Orchestrator & Guardrails

- Self-built routing layer (intent classification → skill dispatch) — avoids locking into any third-party agent framework's hosted API, though open-source orchestration libraries can be vendored and self-hosted.
- **Maker/Checker gate**: any skill output that is financial, legal, or regulatory in nature is marked HUMAN REVIEW REQUIRED by default and cannot auto-execute — inherits the platform's existing Maker/Checker governance requirement directly.
- **PII filter**: scrubs/masks sensitive identifiers in both directions (input logging and output).
- **Refusal policy**: Dhara refuses autonomous financial authorization, autonomous legal filing, and medical/agri-input decisions above a defined risk threshold — by design, not as an afterthought. The same policy governs Krishi SOS: Dhara never substitutes for a human agronomist/vet in a genuine emergency, only speeds the handoff to one.
- **Immutable audit log**: every inference call (input, retrieved context, output, model version, human reviewer decision) logged to the platform-wide audit trail.

## 9. Infra & MLOps Reality

- **Event streaming backbone (Kafka)**: a self-hosted Kafka (or Redpanda, Kafka-API-compatible) cluster is the nervous system connecting the real-time skills — topics for `sos.alerts`, `satellite.ndvi.updates`, `mandi.price.updates`, and `csp.transactions`. Producers (Krishi SOS, the satellite ingestion job, the mandi price puller, the fintech connector) publish; consumers (orchestrator, BI/Decision Support, the RAG indexer) subscribe — this decouples ingestion cadence from model/serving load and keeps the RAG index and BI layer near-real-time without polling.
- **Training**: rented GPU capacity (cloud GPU-hours) for continued pretraining/SFT/DPO runs — renting compute-hours is not the same as calling a third-party model API; weights and data never leave Coopreta's control, only raw compute is rented, same as renting EC2.
- **Inference**: self-hosted serving (a vLLM/TGI-class stack) on Coopreta's own GPU nodes or a dedicated reserved-instance pool — sized for actual Tier 2 traffic, not over-provisioned.
- **Edge**: quantized Tier-1 models ship inside the Android app for offline villages — no network dependency for basic skills; Krishi SOS additionally has an SMS/IVR fallback path that does not depend on the model at all for the most severe, time-critical alerts.
- **CI/CD for models**: every fine-tune run must pass the Dhara-Bench eval gate before promotion — mirrors the platform's existing 45-point "VERIFY→GAP ANALYSIS→RE-VERIFY" discipline, applied to model releases.
- **Cost discipline**: start on rented GPU-hours (OPEX, scales with actual use); move to owned GPU hardware (CAPEX) only once utilization data justifies it. Satellite imagery (Sentinel-2/Bhuvan) and mandi price bulletins (eNAM/Agmarknet) are both free public data sources, so neither adds a licensing cost — only the storage/compute to process them.

## 10. Governance Integration

- Module 14 release gates go through the same 45-point checklist (00-44) as every other module — no separate, looser standard for "AI."
- Status vocabulary for every Dhara capability: PASS / IMPLEMENTED / LIVE VERIFIED / CONDITIONALLY VERIFIED / OPEN / BLOCKED / HUMAN REVIEW REQUIRED / SECURITY GATE BLOCKED. A model that hallucinates on the eval set is OPEN or BLOCKED, never "almost ready."
- Model cards and data lineage records feed directly into the ISO 27001/27701, SOC 2, and DPDP evidence trail already required platform-wide.
- **Hard blocker, repeated from section 1**: do not provision GPU/ML/Kafka infra inside the current AWS foundation until the P0 security gaps (VPC segmentation, prod/staging separation, GuardDuty/Security Hub/Config, least-privilege admin role) are cleared, or an isolated account boundary is carved out specifically for ML/streaming workloads.

## 11. Global Expansion Design

- `i18n/` is structured as **language + regulatory packs**, not hardcoded strings — each pack carries its own fine-tuning data slice, RAG knowledge base slice, and compliance ruleset (a future non-India pack swaps DPDP for that country's data law, swaps CGSS/CGTMSE for the local credit-guarantee scheme).
- Skills are geography-agnostic at the orchestrator level; geography-specific knowledge lives in the RAG index and the language pack, not in skill code — this lets a skill like Grievance & Escalation Drafting, or Mandi Price & Buyer Connect, be reused in a new country by swapping its knowledge pack rather than rewriting it.
- Embedding and core-domain models are multilingual from the first fine-tune (Hindi + English baseline), so adding a new language is a continued-pretraining pass on that language's corpus, not a rebuild.

## 3A. Repo Structure v2 — Added Modules (Kafka, SOS, Satellite, Market Intelligence)

This brings Dhara in line with the Level 12 Global Production Engineering scope now specified — extending the Level 10 programme's five Execution Pods with the event-streaming, emergency-response, remote-sensing, and market-intelligence surface below. Everything in section 3 stays; these are additions:

```
coopreta-dhara/
├── streaming/                       # Kafka/Redpanda — event backbone
│   ├── docker-compose.kafka.yml
│   ├── topics/                      # topic definitions + retention policy
│   │   ├── sos.alerts/
│   │   ├── satellite.ndvi.updates/
│   │   ├── mandi.price.updates/
│   │   └── csp.transactions/
│   ├── producers/
│   └── consumers/
├── data/ingestion/
│   ├── satellite/                   # Sentinel-2 / ISRO Bhuvan pull + NDVI/NDMI compute
│   └── mandi_prices/                # eNAM / Agmarknet public bulletin pull
├── skills/
│   ├── krishi_sos/                  # emergency triage + multi-channel escalation
│   ├── satellite_crop_intel/
│   ├── market_price_buyer_connect/
│   ├── market_research_demand/
│   ├── customer_finder/
│   └── community_social/
└── channels/
    └── sms_ivr_fallback/            # zero-model-dependency emergency path
```

Satellite and mandi-price connectors get their own data-source card in `docs/model-cards/`, not a model card — they ingest public data rather than train on it, so their governance evidence is about data provenance, not model lineage.

## 12. Phased Roadmap

&#91;embedded content: Dhara roadmap · 5 phases\]

Dhara-0/1 can start now; Dhara-2 onward needs the Agriculture/PACS/FPO/Lending/BI platform phases live. Satellite, SOS, and market-intelligence skills land inside Dhara-3/4 once the orchestrator and Kafka backbone are wired — AI does not front-run the platform it depends on.

## 13. Budget Reality

Rough, phased, OPEX-first (planning ranges, not quotes):

- **Dhara-0/1** (data pipelines + RAG MVP on a rented open-weight model): lean — mostly engineering time plus modest cloud GPU rental for embedding/inference, no training spend yet.
- **Dhara-2** (first fine-tune): a single continued-pretraining + SFT run on a 7-13B model is feasible on rented multi-GPU cloud instances for a bounded number of GPU-hours — orders of magnitude cheaper than frontier pretraining, but still a real line item that should be sized against actual revenue (vermicompost Year-1 EBITDA, fintech CSP income) before committing, not funded speculatively.
- **Dhara-3+**: scales with usage — inference cost before training cost; invest in owned GPU hardware only once a rented-GPU cost curve justifies it. The Kafka cluster, satellite ingestion, and mandi price pulls are all cheap relative to training — modest compute/storage, no new licensing (both satellite and price data are public).

Given Coopreta's current capital position (vermicompost CAPEX, stalled CGTMSE loan appraisal), the right posture is: fund Dhara-0/1 from engineering time now, and gate Dhara-2's training spend on either the loan resolution or a small dedicated grant/DPIIT innovation fund, rather than diverting vermicompost or fintech working capital into GPU rental.

## 14. Team / Roles (extends the 29-role model)

Add to the **Agentic AI/Experience/Offline UX** Execution Pod: an ML infra/MLOps engineer, an applied NLP/LLM fine-tuning engineer, a RAG/retrieval engineer, a streaming/data engineer (owns the Kafka backbone), a GIS/remote-sensing engineer (satellite ingestion + NDVI pipeline), an evaluation engineer (owns Dhara-Bench), a market/demand analyst (Market Research, Customer Finder), and a DPDP/AI-governance compliance role shared with the existing GRC pod. An on-call agronomist/veterinarian relationship (even part-time/retainer) is required to validate Krishi SOS escalations — this is a domain-expert role, not an engineering one, but it is load-bearing for that skill's safety. Devin continues as the 29th autonomous execution role across all of the above, under the same 45-point spine.

## 15. Success Metrics — the real "10x"

Not a general leaderboard score. Published per release, per skill:

- Dhara-Bench score vs. the ChatGPT baseline on held-out Coopreta documents — the target is to be materially ahead on domain tasks, since that is the defensible claim.
- Grievance-drafting turnaround time (human-reviewed) vs. manual drafting time.
- RAG citation accuracy — does the cited clause actually say what Dhara claims.
- Krishi SOS mean-time-to-human-escalation, and zero incidents of a severe alert not reaching a human.
- Satellite alert precision/recall against farmer-reported ground truth.
- Mandi Price & Buyer Connect: buyer-lead conversion rate, and price-citation accuracy against the source bulletin.
- Zero incidents of autonomous financial/legal action without Maker/Checker sign-off.
- Offline/edge skill availability in zero-connectivity test villages.

## 16. Immediate Next Steps (2-4 weeks)

1. Stand up the `coopreta-dhara` repo with the structure in sections 3 and 3A; write `GOVERNANCE.md` referencing the existing constitution.
2. Start Dhara-0: pull the legal escalation corpus and vermicompost SOPs into the ingestion pipeline first — they're the most immediately valuable and already exist as documents.
3. Resolve, or formally carve out, an isolated ML/streaming account boundary against the AWS P0 findings before any GPU or Kafka workload is scheduled.
4. Pick the open-weight base model family for the Core Domain Model (Llama/Mistral/Qwen-class) and stand up self-hosted inference for a Dhara-1 RAG MVP — no fine-tuning yet, prove the RAG + skill pattern first.
5. Draft the Dhara-Bench v0 held-out set from 20-30 real Coopreta documents (escalation letters, KCC forms, vermicompost filings) — this becomes the yardstick for every claim made about this system from here on.
6. Stand up a single-node Kafka (or Redpanda) dev cluster and confirm the four topics can be created and consumed end-to-end.
7. Shortlist a satellite data source (Sentinel Hub free tier vs. ISRO Bhuvan) and a mandi-price source (eNAM vs. Agmarknet), and confirm each one's access terms in writing before building against it.
8. Line up the on-call agronomist/vet relationship needed to validate Krishi SOS before that skill goes anywhere near a real farmer.

## 17. Cursor-Based Phase-Wise Development Plan — Prompts & Commands

Where sections 1–16 are the engineering spec Devin executes under Coopreta One's 45-point discipline, this section is the hands-on build plan for **Cursor** — ready-to-paste prompts plus the shell commands around them, phase by phase. Paste each prompt into Cursor's Composer/Chat inside the `coopreta-dhara` repo; run the commands in a terminal alongside it.

### Phase 0 — Repo & Governance Scaffold

**Cursor prompt:**

> Create a monorepo named `coopreta-dhara` with top-level folders: `docs, infra, data, models, rag, orchestrator, skills, channels, i18n, security, tests, scripts, streaming`. Add a `README.md` describing it as Coopreta's self-hosted, sovereign agentic AI system — Module 14 of Coopreta One. Add a `GOVERNANCE.md` stating the 45-point checklist status vocabulary (PASS / IMPLEMENTED / LIVE VERIFIED / CONDITIONALLY VERIFIED / OPEN / BLOCKED / HUMAN REVIEW REQUIRED / SECURITY GATE BLOCKED) and that no capability may claim a status without evidence. Add a stub `README.md` inside every folder explaining its purpose. Set up Python tooling: `pyproject.toml` with `black`, `ruff`, `pytest`; a `pre-commit` config running both on every commit.

**Commands:**

```
git init coopreta-dhara && cd coopreta-dhara
mkdir -p docs infra data models rag orchestrator skills channels i18n security tests scripts streaming
pip install pre-commit black ruff pytest
pre-commit install
git add -A && git commit -m "Phase 0: repo + governance scaffold"
```

### Phase 1 — Data Ingestion & RAG MVP

**Cursor prompt:**

> Implement ingestion connectors under `data/ingestion/` for: `legal_escalation_corpus` (PDF/DOCX text extraction with metadata: doc\_type, date, case\_ref), `vermicompost_ops` (structured CSV/financial doc parsing), `government_schemes` (PDF parsing of public NABARD/RKVY/CGTMSE scheme documents). Output cleaned, chunked text with metadata to `data/pipelines/output/`. Then build a RAG service under `rag/`: a self-hosted Postgres + pgvector store, a self-hosted multilingual sentence-embedding model for indexing, a retriever, and a FastAPI app exposing `POST /query` that returns an answer grounded in retrieved chunks with inline citations to `doc_type` + `date`.

**Commands:**

```
docker compose -f infra/docker-compose.pgvector.yml up -d
pip install fastapi uvicorn sentence-transformers psycopg2-binary pgvector pypdf python-docx
uvicorn rag.app:app --reload --port 8000
```

### Phase 2 — Core Domain Model Fine-Tune & Dhara-Bench

**Cursor prompt:**

> Set up a LoRA fine-tuning pipeline under `models/sft/` using Hugging Face `transformers` + `peft` on a 7-13B open-weight base checkpoint. Build a JSONL instruction-dataset loader reading from `data/annotation/sft_dataset.jsonl`. Write `train_sft.py`, configurable via a YAML in `models/sft/configs/`, for a single multi-GPU node. Build `models/eval/dhara_bench.py`: an evaluation harness that runs both the fine-tuned model and a reference baseline against a held-out folder of 20-30 real Coopreta documents, scoring factual accuracy, Coopreta-style match, and citation correctness, and writes a model card to `docs/model-cards/`.

**Commands:**

```
pip install transformers peft accelerate bitsandbytes datasets
python models/sft/train_sft.py --config models/sft/configs/7b_lora.yaml
python models/eval/dhara_bench.py --model-path ./checkpoints/sft-v1 --holdout data/eval/holdout_v0/
```

### Phase 3 — Orchestrator, All 14 Skills, Kafka Wiring

**Cursor prompt:**

> Build the orchestrator under `orchestrator/`: an intent router dispatching to skill modules in `skills/`, each implementing a common `Skill` interface (`name`, `input_schema`, `guardrail_tier`, `run(context)`). Implement all 14 Dhara Skills as separate packages under `skills/` (krishi\_salah, fintech\_sahayak, pacs\_kcc\_docs, grievance\_escalation, vermicompost\_ops, khet\_se\_baat\_content, legal\_compliance\_draft, bi\_decision\_support, krishi\_sos, satellite\_crop\_intel, market\_price\_buyer\_connect, market\_research\_demand, customer\_finder, community\_social). Add Maker/Checker middleware in `orchestrator/guardrails/` that intercepts any output tagged `guardrail_tier="human_review"` and queues it instead of returning it directly. Stand up a single-node Kafka (or Redpanda) cluster under `streaming/` with topics `sos.alerts`, `satellite.ndvi.updates`, `mandi.price.updates`, `csp.transactions`; wire `krishi_sos` to publish to `sos.alerts` and the orchestrator to consume it and trigger WhatsApp + SMS/IVR notification.

**Commands:**

```
docker compose -f streaming/docker-compose.kafka.yml up -d
python streaming/topics/create_topics.py
pip install confluent-kafka
pytest tests/integration/test_orchestrator_dispatch.py
```

### Phase 4 — Satellite Intelligence, Edge Model, DPO

**Cursor prompt:**

> Build a satellite ingestion job under `data/ingestion/satellite/` pulling Sentinel-2 L2A imagery (via Sentinel Hub's free tier or ISRO Bhuvan) for Coopreta's registered plot coordinates, computing NDVI/NDMI weekly, publishing results to `satellite.ndvi.updates` and storing them in the Data Fabric. Implement the `satellite_crop_intel` skill to turn NDVI trends into plain-language advisories, citing imagery date and confidence. Implement DPO preference-tuning in `models/preference/` from Coopreta-curated preference pairs. Quantize the fine-tuned model to GGUF int4 for on-device use and scaffold `channels/android_offline/` with a `llama.cpp`-based local inference path.

**Commands:**

```
pip install sentinelhub rasterio numpy
python data/ingestion/satellite/pull_and_compute_ndvi.py --plots data/plots.csv
python models/distillation/quantize_gguf.py --model ./checkpoints/sft-v1 --quant int4
```

### Phase 5 — Market Intelligence & Multi-Tenant RAG

**Cursor prompt:**

> Build `market_price_buyer_connect`: ingest daily public eNAM/Agmarknet price bulletins into `mandi.price.updates`, and match buyer leads against seller inventory (vermicompost, Kalmegh, Dr. Bacto's line) using Coopreta's own CRM data. Build `market_research_demand` and `customer_finder` on top of the Economic Graph/BI layer. Add multi-tenant partitioning to the RAG vector store (partition key = Party/Organization id) so a second FPO/PACS customer's data is isolated from Coopreta's own.

**Commands:**

```
python data/ingestion/mandi_prices/pull_enam_daily.py
alembic revision --autogenerate -m "add tenant_id partition to rag_chunks"
alembic upgrade head
```

### Phase 6 — Global Language/Regulatory Pack

**Cursor prompt:**

> Scaffold a new pack under `i18n/` by copying `i18n/_template/` to the target geography's code. Wire a continued-pretraining data slice and a RAG knowledge slice for that geography's credit-guarantee scheme and data-protection law, with no change to any skill's code — only new data and a new pack config.

**Commands:**

```
cp -r i18n/_template i18n/<new-geo-code>
python scripts/validate_i18n_pack.py i18n/<new-geo-code>
```

Each phase's commit should close with the same discipline as the rest of Coopreta One: run the relevant tests, update the phase's status in `GOVERNANCE.md` using the restricted vocabulary, and never mark a phase LIVE VERIFIED on Cursor's say-so alone — the same independent-evidence bar applies whether Devin or Cursor did the work.

## 18. Complete Technology Stack — Foundation to Deployment

Every row below is a concrete choice, not an option list — this is what gets built, chosen so nothing in the request path calls a third-party AI API:

| Layer | Choice | Reference |
| --- | --- | --- |
| Server OS | Ubuntu 24.04 LTS | matches the existing Coopreta One AWS base |
| Core language (orchestrator, RAG, skills, training) | Python 3.11 | — |
| Backend API framework | FastAPI (async, auto-OpenAPI, Pydantic validation) | github.com/fastapi/fastapi |
| Admin / Maker-Checker dashboard | React 18 + TypeScript + Next.js 14, Tailwind CSS | github.com/vercel/next.js — reuses coopreta.in's Manrope/DM Sans/Tailwind design system |
| Android offline app | Kotlin + Jetpack Compose, on-device inference via llama.cpp JNI bindings | github.com/ggml-org/llama.cpp |
| Relational + vector store | PostgreSQL 16 + pgvector extension | github.com/pgvector/pgvector |
| Cache / session / job broker | Redis 7 | — |
| Event streaming | Redpanda — Kafka-API-compatible, single binary, lower ops overhead than Kafka+ZooKeeper | github.com/redpanda-data/redpanda |
| Background jobs ("JES") | Celery + Redis broker | github.com/celery/celery |
| RAG orchestration | LlamaIndex, self-hosted | github.com/run-llama/llama\_index |
| Embedding model | self-hosted multilingual encoder (e.g. BAAI/bge-m3), served via sentence-transformers | github.com/UKPLab/sentence-transformers |
| LLM serving (inference) | vLLM — self-hosted, OpenAI-compatible local API, never leaves Coopreta's network | github.com/vllm-project/vllm |
| Fine-tuning (SFT/LoRA/DPO) | axolotl, or LLaMA-Factory | github.com/axolotl-ai-cloud/axolotl · github.com/hiyouga/LLaMA-Factory |
| Containers | Docker + Docker Compose (dev); Kubernetes/k3s (staging/prod) | — |
| CI/CD | GitHub Actions — ordinary dev tooling, not an AI/model dependency, so it stays in scope | — |
| Secrets management | HashiCorp Vault | github.com/hashicorp/vault |
| Observability | Prometheus + Grafana + Loki | github.com/prometheus/prometheus · github.com/grafana/grafana |
| Agent tool-calling layer | Model Context Protocol — official Python SDK + reference servers, self-hosted | github.com/modelcontextprotocol/python-sdk · github.com/modelcontextprotocol/servers |

Every item above is either infrastructure/dev tooling (CI/CD, containers, observability — no AI capability, so sovereignty doesn't apply) or a self-hosted open-source component Coopreta runs on its own machines — nothing here is a paid third-party AI API call.

## 19. MCP (Model Context Protocol) Integration

MCP is an open protocol (not a vendor service) for letting an LLM agent call external tools through a standard interface. Dhara's orchestrator is the MCP **client**; Coopreta builds and self-hosts several MCP **servers**, each wrapping one internal system, so a skill calls a standard tool instead of a bespoke integration:

| MCP server | Wraps | Feeds these skills |
| --- | --- | --- |
| `mcp-crm` | Coopreta's CRM/customer data | Customer Finder, Mandi Price & Buyer Connect |
| `mcp-ledger` | the Economic Graph / Ledger (Module 13) | BI/Decision Support, Fintech Sahayak |
| `mcp-documents` | the Document/Evidence store (Module 02) | PACS/KCC Documentation, Grievance & Escalation Drafting |
| `mcp-agri-data` | farm/plot/satellite records | Krishi Salah, Satellite Crop Intelligence, Krishi SOS |
| `mcp-market` | mandi price feed + CRM inventory | Mandi Price & Buyer Connect, Market Research & Demand Signal Engine |

The target production design is for these services to use the official Model Context Protocol Python SDK, stay on the private network, and expose manifest-declared tools with auditable access controls. **Current repository state:** all five `server.py` entry points speak MCP over local stdio and return development-contract responses marked `OPEN`; none is connected to its business backend, deployed on the orchestrator's private subnet, or protected by production service-to-service controls. `.cursor/mcp.json` and `.codex/config.toml` configure local developer launches only. A successful local handshake is not evidence of a live integration.

## 3B. Repo Structure v3 — MCP Servers

```
coopreta-dhara/
├── mcp-servers/
│   ├── mcp-crm/
│   ├── mcp-ledger/
│   ├── mcp-documents/
│   ├── mcp-agri-data/
│   └── mcp-market/
│       ├── server.py
│       ├── tools/
│       ├── manifest.yaml
│       └── tests/
```

## 20. Security Architecture (Full Depth)

- **Auth**: JWT access tokens (15-minute expiry) + refresh tokens (7-day expiry) for human users (Maker/Checker dashboard, admin console). Service-to-service calls (orchestrator ↔ skills ↔ MCP servers) use mutual TLS, not JWT — no bearer token to leak between internal services.
- **Secrets**: HashiCorp Vault for every credential and API key; nothing secret ever committed to git; database credentials are short-lived and dynamically issued, not static passwords.
- **Encryption**: TLS 1.3 everywhere in transit. Disk-level encryption at rest for every Postgres/Kafka volume. PII fields (farmer phone numbers, any Aadhaar fragments) get additional field-level encryption beyond disk encryption.
- **RBAC + ABAC**: every API call is checked against both a role (agronomist, loan officer, admin, field agent) and an attribute (tenant/Party id, the skill's guardrail tier) — enforced as shared middleware, never as ad hoc per-endpoint logic that drifts out of sync.
- **OWASP ASVS Level 2** checklist mapped and evidenced per release in `docs/model-cards/` — part of the same 45-point evidence trail as every other module.
- **Perimeter**: rate limiting + a WAF in front of every public-facing channel endpoint (WhatsApp/web-widget webhooks) — these are the only components with any public exposure at all.
- **Supply chain**: Dependabot/Trivy dependency and container-image scanning in CI, blocking on any high/critical finding before deploy.
- **Network**: GPU, Kafka, and database nodes sit in private subnets with no public IP, inside the isolated ML/streaming account boundary from sections 1 and 10 — this is the same boundary that has to exist before any of this infrastructure is provisioned.

## 21. Database Schema — Core Dhara Tables

Simplified DDL for the tables specific to Module 14 (these sit alongside, and reference, the platform's own Party/Organization/Document tables from Modules 01-02 — never duplicate those, only reference their ids):

```sql
-- RAG chunk store (pgvector)
CREATE TABLE rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,              -- Party/Organization id, for multi-tenant isolation
  source_doc_type TEXT NOT NULL,        -- 'legal_escalation' | 'vermicompost_sop' | 'govt_scheme' | ...
  source_ref TEXT NOT NULL,             -- pointer to the Document/Evidence record
  as_of_date DATE,
  content TEXT NOT NULL,
  embedding VECTOR(1024) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON rag_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON rag_chunks (tenant_id);

-- Model registry / model cards
CREATE TABLE model_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_name TEXT NOT NULL,             -- e.g. 'dhara-core-7b'
  version TEXT NOT NULL,
  base_checkpoint TEXT NOT NULL,
  training_data_lineage JSONB NOT NULL, -- dataset versions used
  dhara_bench_score NUMERIC,
  chatgpt_baseline_score NUMERIC,
  status TEXT NOT NULL,                 -- PASS / OPEN / BLOCKED / ... (section 10 vocabulary)
  published_at TIMESTAMPTZ DEFAULT now()
);

-- Every skill invocation, for the audit trail
CREATE TABLE skill_invocations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  skill_name TEXT NOT NULL,
  guardrail_tier TEXT NOT NULL,         -- 'auto' | 'human_review'
  input JSONB NOT NULL,
  retrieved_context JSONB,
  output JSONB,
  model_version TEXT,
  reviewer_id UUID,                     -- null until a human acts, for human_review tier
  reviewer_decision TEXT,               -- 'approved' | 'rejected' | null
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Krishi SOS
CREATE TABLE sos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  plot_id UUID,
  category TEXT NOT NULL,               -- 'crop_disease' | 'pest' | 'weather' | 'livestock'
  severity TEXT NOT NULL,
  channel TEXT NOT NULL,                -- 'app' | 'whatsapp' | 'ivr_sms'
  escalated_to TEXT,                    -- agronomist/vet/extension-officer contact
  escalated_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Satellite readings
CREATE TABLE satellite_ndvi_readings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plot_id UUID NOT NULL,
  image_date DATE NOT NULL,
  ndvi NUMERIC,
  ndmi NUMERIC,
  source TEXT NOT NULL,                 -- 'sentinel-2' | 'bhuvan'
  confidence NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Mandi prices
CREATE TABLE mandi_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  commodity TEXT NOT NULL,
  mandi_name TEXT NOT NULL,
  price_date DATE NOT NULL,
  min_price NUMERIC,
  max_price NUMERIC,
  modal_price NUMERIC,
  source TEXT NOT NULL,                 -- 'enam' | 'agmarknet'
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Buyer leads
CREATE TABLE buyer_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  commodity TEXT NOT NULL,
  buyer_name TEXT NOT NULL,
  contact TEXT,
  match_score NUMERIC,
  status TEXT NOT NULL,                 -- 'new' | 'contacted' | 'converted' | 'dropped'
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Maker/Checker queue
CREATE TABLE maker_checker_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invocation_id UUID NOT NULL REFERENCES skill_invocations(id),
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending' | 'approved' | 'rejected'
  reviewer_id UUID,
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## 22. Kafka/Redpanda Topic Schemas

| Topic | Key | Value (JSON) | Partitions | Retention | Producers → Consumers |
| --- | --- | --- | --- | --- | --- |
| `sos.alerts` | `plot_id` | `{category, severity, channel, tenant_id, created_at}` | 6 | 30 days | Krishi SOS skill → orchestrator notifier, BI |
| `satellite.ndvi.updates` | `plot_id` | `{ndvi, ndmi, image_date, source, confidence}` | 6 | 90 days | satellite ingestion job → Satellite Crop Intelligence skill, RAG indexer |
| `mandi.price.updates` | `commodity+mandi_name` | `{min_price, max_price, modal_price, price_date, source}` | 3 | 180 days | mandi price puller → Mandi Price & Buyer Connect, Market Research |
| `csp.transactions` | `tenant_id` | `{txn_type, amount, status, timestamp}` (PII-scrubbed) | 12 | 400 days (compliance) | fintech connector → Fintech Sahayak, BI, fraud signals |

All four topics use Avro or JSON Schema registered in a schema registry (Redpanda's built-in one) so a producer can't publish a payload a consumer wasn't built for — schema changes go through the same 45-point review as any other interface change.

## 23. Background Jobs ("JES" — Job Execution Service)

Celery workers, scheduled via Celery Beat, Redis as the broker:

| Job | Cadence | Does |
| --- | --- | --- |
| `pull_satellite_imagery` | weekly | Sentinel-2/Bhuvan pull + NDVI/NDMI compute per registered plot |
| `pull_mandi_prices` | daily | eNAM/Agmarknet bulletin ingestion |
| `reindex_rag_corpus` | nightly | re-embeds any document changed that day |
| `run_dhara_bench` | on every model promotion | runs the eval harness, blocks promotion on failure |
| `expire_maker_checker_queue` | hourly | flags anything pending human review past its SLA for escalation |
| `rotate_vault_db_credentials` | every 24h | rotates short-lived DB credentials |

## 24. API Specification (REST, FastAPI/OpenAPI)

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/query` | JWT | RAG query, returns a grounded answer + citations |
| POST | `/skills/{skill_name}/invoke` | JWT + ABAC tenant check | dispatches to a Dhara Skill |
| POST | `/sos/alert` | JWT or channel webhook signature | raises a Krishi SOS alert |
| GET | `/satellite/ndvi/{plot_id}` | JWT | latest NDVI/NDMI reading for a plot |
| GET | `/mandi/prices` | JWT | current mandi price snapshot |
| GET | `/buyers/match` | JWT | ranked buyer leads for a commodity |
| GET | `/admin/maker-checker` | JWT (reviewer role) | lists pending human-review items |
| POST | `/admin/maker-checker/{id}/approve` | JWT (reviewer role) | approves a queued action |
| POST | `/admin/maker-checker/{id}/reject` | JWT (reviewer role) | rejects a queued action |
| GET | `/health` | none | liveness/readiness probe |
| GET | `/metrics` | internal-only | Prometheus scrape endpoint |

The full OpenAPI schema is auto-generated by FastAPI at `/openapi.json` and published to `docs/` on every release.

## 25. End-to-End Integration & Deployment

**Local dev** — one `docker-compose.yml` brings up Postgres+pgvector, Redis, Redpanda, and the FastAPI app with hot-reload; `make dev` is the one command a new engineer needs.

**CI (GitHub Actions)** on every PR: lint (`ruff`, `black --check`) → unit tests (`pytest`) → dependency/image scan (Trivy) → on a model-affecting change, the Dhara-Bench eval gate (section 5) must pass before merge is allowed.

**CD**: merge to `main` builds and pushes a container image, then deploys to **staging** (k3s) automatically; **production** deploy is a manual promotion gate requiring a human to confirm the 45-point checklist status is PASS/LIVE VERIFIED for every touched capability — mirrors the platform's existing Progressive Canary Delivery (dark-launch → 5% canary → 25% → 100%) from the Coopreta One Level 10/12 program.

**Topology**: all of the above sits inside the isolated ML/streaming account boundary (sections 1, 10, 20) — private subnets, no public IP on GPU/Kafka/DB nodes, only the channel webhooks (WhatsApp, web widget) exposed behind the WAF.

This closes the loop from section 0's premise: every piece above is either open-source software Coopreta runs on its own infrastructure, or public government data (satellite, mandi prices) — nothing in this stack is a paid third-party AI API call.
