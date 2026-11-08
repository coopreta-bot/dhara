---
name: dhara-module-14
description: >-
  Applies Coopreta Dhara Module 14 rules — sovereign self-hosted models, the
  status vocabulary, Maker/Checker gates, and the repo map. Use when editing
  this repository, planning a Dhara phase, or answering questions about RAG,
  skills, MCP, Redpanda, or model training.
---

# Dhara Module 14

## Instructions

1. Read `GOVERNANCE.md` and `PLAN.md` before changing scope or status.
2. Keep the phase order in `docs/plan/phases.md`. Do not start fine-tuning, satellite ingestion, or Krishi SOS against real farmers while those rows are BLOCKED.
3. Put design changes in `docs/adr/` when they change sovereignty, tenancy, or the tool layer.
4. When a task adds a product skill, use the `add-dhara-skill` skill. When it adds a tool server, use `add-mcp-server`.
5. Leave status as OPEN unless an artifact in the tree is the evidence. Then the highest honest word is IMPLEMENTED. LIVE VERIFIED needs an independent check.

## Repo map

- Product skills: `skills/*/manifest.yaml`
- MCP servers: `mcp-servers/*/manifest.yaml`
- Tables: `docs/architecture/schema.sql`
- Topics: `docs/architecture/topics.md`
- HTTP contract: `docs/architecture/api.md`
- Setup: `docs/setup/README.md`
