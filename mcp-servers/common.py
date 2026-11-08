"""Start a Dhara MCP server from the folder's manifest.yaml.

Tools are development contracts. They do not call a live CRM, ledger, or market.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from mcp.server.mcpserver import MCPServer


def serve(folder: Path) -> None:
    manifest = yaml.safe_load((folder / "manifest.yaml").read_text(encoding="utf-8"))
    name = str(manifest["name"])
    mcp = MCPServer(name)

    @mcp.tool()
    def server_manifest() -> str:
        """Return this server's manifest: tools, guardrail, and what it wraps."""
        return json.dumps(manifest, indent=2)

    for tool in manifest.get("tools", []):
        tool_name = str(tool["name"])
        tier = str(tool.get("guardrail_tier", manifest.get("default_guardrail_tier", "human_review")))
        _register(mcp, name, tool_name, tier, str(manifest.get("wraps", "")).strip())

    mcp.run(transport="stdio")


def _register(mcp: MCPServer, server: str, tool_name: str, tier: str, wraps: str) -> None:
    def handler(query: str = "") -> str:
        return json.dumps(
            {
                "server": server,
                "tool": tool_name,
                "guardrail_tier": tier,
                "status": "OPEN",
                "wraps": wraps,
                "query": query,
                "detail": (
                    "The Coopreta system this server wraps is not connected. "
                    "Use this response as the tool contract while developing."
                ),
            },
            indent=2,
        )

    handler.__name__ = tool_name
    handler.__doc__ = (
        f"{tool_name} on {server}. Guardrail tier: {tier}. "
        "Live backend is not connected; returns the development contract."
    )
    mcp.tool()(handler)
