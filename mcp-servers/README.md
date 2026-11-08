# MCP servers

Five local stdio MCP contract servers are implemented from their manifests. Each exposes contract tools that return `status: OPEN`; none is connected to its CRM, ledger, document, farm, or market backend.

The orchestrator is the intended product MCP client. `.cursor/mcp.json` and `.codex/config.toml` also configure local developer sessions to launch the contract servers. That configuration is not a production deployment or proof of private-network isolation. Production services must remain internal-only and use the planned service-to-service security controls.

Status: IMPLEMENTED for the local protocol contracts; OPEN for backend integrations and production deployment. Nothing here is LIVE VERIFIED.
