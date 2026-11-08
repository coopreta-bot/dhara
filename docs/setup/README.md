# Setup

Phase 0 prepares the tree. It does not start Postgres, Redpanda, vLLM, or Vault.

## Python

Requires Python 3.11.

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pre-commit install
```

`make lint` and `make test` need GNU make, which is optional on Windows. The same commands are `ruff check .`, `black --check .`, and `pytest`.

`make dev` exits on purpose. The compose stack is Phase 1.

## What else was added

| Piece | Where | State |
| --- | --- | --- |
| Editor recommendations | `.vscode/extensions.json` | Listed, not installed. Install from the editor. |
| Cursor rule | `.cursor/rules/dhara-sovereignty.mdc` | Always on for this repo |
| Project skills | `.cursor/skills/` | See [skills.md](skills.md) |
| MCP | `mcp-servers/` and [mcp.md](mcp.md) | Five local stdio MCP contract servers; business backends remain OPEN. |
| Plugin notes | [plugins.md](plugins.md) | No marketplace plugin was named in the blueprint, so none was installed. |

## Git

Initialize a repository when you want history. Do not commit `.env`, weights, or raw farmer documents. Those patterns are in `.gitignore`, and a gitignore is not a substitute for keeping source files out of the folder.
