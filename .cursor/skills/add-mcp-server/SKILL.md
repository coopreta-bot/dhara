---
name: add-mcp-server
description: >-
  Scaffolds a self-hosted Coopreta Dhara MCP server under mcp-servers/ with a
  manifest and a local stdio contract server. Use when the user says add MCP, new
  MCP server, or a skill needs a tool that is not crm, ledger, documents,
  agri-data, or market.
disable-model-invocation: true
---

# Add an MCP server

## Instructions

1. Create `mcp-servers/<name>/` with `manifest.yaml`, `server.py`, `tools/README.md`, and `tests/README.md`.
2. Manifest fields: `name`, `status: OPEN`, `transport: stdio`, `exposure: internal-only`, `wraps`, `feeds`, `default_guardrail_tier`, and a `tools` list. Each tool has `name`, `status: OPEN`, and `guardrail_tier`.
3. Implement `server.py` as a stdio MCP contract server using `mcp-servers/common.py:serve`. Contract tools must clearly return `status: OPEN` and must not imply a business backend is connected.
4. Smoke-test the MCP handshake and `tools/list`. A passing protocol check does not make the business integration LIVE VERIFIED.
5. Document the server and its contract-only status in `docs/setup/mcp.md`. Add it to `.cursor/mcp.json` and `.codex/config.toml` only after the smoke test; update `docs/setup/mcp.json.example` as a local-client example. These configs are not production deployment.
6. Keep servers off the public internet. Local stdio is the current transport; production network deployment requires the planned internal boundary and mutual TLS.
7. Record the protocol contract as IMPLEMENTED and the unconnected business integration as OPEN in `GOVERNANCE.md`.
