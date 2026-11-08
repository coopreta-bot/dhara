# Plugins

The blueprint does not name a Cursor marketplace plugin. This scaffold does not install one.

Use `/add-plugin` in Cursor only for a plugin you have already chosen. Prefer plugins that stay on the machine: Python, YAML, Docker, and Markdown. Do not add a plugin whose job is to call a hosted chat or embeddings API from the Dhara request path. That would break [ADR 0001](../adr/0001-model-sovereignty.md).

Editor recommendations already live in `.vscode/extensions.json`:

- Python
- Ruff
- Black
- Docker
- YAML
- Markdown

Install those from the Extensions view. Installation was not run from this scaffold, so their status stays OPEN.
