# MCP setup

Five servers are specified in [ADR 0002](../adr/0002-mcp-tool-layer.md). Each folder under `mcp-servers/` has:

- `manifest.yaml` — tools, exposure, guardrail tier
- `server.py` — a stdio MCP contract server
- `tools/` and `tests/` — extension points; no business backend or server-specific behavior is connected

The five `server.py` files speak MCP and expose `server_manifest` plus the tools declared in their manifests. Tool calls return development-contract data with `status: OPEN`; they do not read or write CRM, ledger, documents, farm, or market systems. A successful MCP handshake proves only that the local protocol contract works—not that a business integration is live.

The five existing servers are configured for local stdio launch in `.cursor/mcp.json` and `.codex/config.toml`. These are developer-tool configurations, not production deployment or network exposure. Keep MCP servers off the public internet. Production service-to-service auth is intended to use mutual TLS; the current local stdio contract servers do not implement that deployment boundary.

Use [mcp.json.example](mcp.json.example) as a reference when configuring a local client. Add a new server to an active client config only after its MCP handshake and `tools/list` contract have been smoke-tested, and document that it is contract-only until its backend is connected.

| Server | Wraps | Skills |
| --- | --- | --- |
| mcp-crm | CRM | Customer Finder, Mandi Price and Buyer Connect |
| mcp-ledger | Ledger / Economic Graph | BI / Decision Support, Fintech Sahayak |
| mcp-documents | Document store | PACS/KCC, Grievance and Escalation |
| mcp-agri-data | Plots and satellite readings | Krishi Salah, Satellite Crop Intelligence, Krishi SOS |
| mcp-market | Mandi prices and inventory | Mandi Price and Buyer Connect, Market Research |

Add a server by following the project skill `add-mcp-server`.
