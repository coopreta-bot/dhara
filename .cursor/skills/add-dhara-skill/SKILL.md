---
name: add-dhara-skill
description: >-
  Adds a Coopreta Dhara product skill under skills/ with a manifest, README,
  and registry notes. Use when the user says add skill, new Dhara skill, or
  names a workflow that should become a skill module.
disable-model-invocation: true
---

# Add a Dhara skill

## Instructions

1. Pick a lowercase snake_case id. Create `skills/<id>/`.
2. Write `manifest.yaml` with `name`, `display_name`, `status: OPEN`, `guardrail_tier` (`auto` or `human_review`), `purpose`, `guardrail`, `tools` (MCP server ids), and `data_scope`.
3. Write a short `README.md` that repeats the guardrail in plain language.
4. If the output can file, pay, prescribe, publish to other farmers, or bind a trade, set `guardrail_tier: human_review`.
5. Add a row to the table in `docs/setup/skills.md` and to the capability register in `GOVERNANCE.md` as OPEN.
6. Do not implement tools inside the skill. Declare MCP servers. If the server does not exist, add it with `add-mcp-server` first.
7. Do not register the skill as runnable. The orchestrator code is not built yet.

## Example manifest

```yaml
name: example_skill
display_name: Example Skill
status: OPEN
guardrail_tier: human_review
purpose: |
  One sentence.
guardrail: |
  What a human must approve.
tools:
  - mcp-documents
data_scope:
  - government_schemes
```
