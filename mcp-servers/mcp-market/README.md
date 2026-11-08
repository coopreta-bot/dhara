# mcp-market

Wraps: Mandi price feed and CRM inventory.

Feeds: Mandi Price and Buyer Connect, Market Research and Demand Signal.

The local stdio MCP server exposes manifest-declared contract tools. Calls return development responses marked `OPEN`; mandi-price and inventory backends are not connected. This is not a production service or a private-network deployment. See `manifest.yaml` and `docs/setup/mcp.md`.

Protocol contract: IMPLEMENTED. Backend integration and production deployment: OPEN. Nothing here is LIVE VERIFIED.
