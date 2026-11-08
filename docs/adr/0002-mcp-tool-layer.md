# ADR 0002 — MCP as the tool layer

Status: accepted for the design. Five local stdio MCP contract servers are implemented; business-system integrations and production deployment remain OPEN.

## Context

Each skill needs CRM, ledger, documents, farm plots, or mandi data. One-off HTTP clients would drift apart and would be hard to audit.

## Decision

The orchestrator is intended to be the MCP client for five internal servers: `mcp-crm`, `mcp-ledger`, `mcp-documents`, `mcp-agri-data`, and `mcp-market`. Each server has a manifest listing its tools and guardrail tiers. The current `server.py` entry points use the official MCP Python SDK and expose contract tools that return `OPEN` development responses; they are not connected to business systems. `.cursor/mcp.json` and `.codex/config.toml` launch these contract servers locally over stdio. A future production deployment must keep servers on the private network and apply the planned service-to-service controls; local configuration does not establish that deployment.

## Consequences

- A new integration adds a tool on an existing server, or a new server folder, instead of a private client inside a skill.
- Skills declare tools in `manifest.yaml`. The registry refuses a tool the skill did not declare.
- A successful local MCP handshake verifies the protocol contract only. It does not verify a backend, authorization boundary, or production service.
