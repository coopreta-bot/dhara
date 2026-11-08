# Skills

Two different "skills" exist in this repo. Do not mix them.

## Dhara Skills (product)

`skills/<id>/manifest.yaml` is what the orchestrator will load. Fourteen skills from the blueprint are declared. None of them run. Guardrail tiers:

| Skill | Tier |
| --- | --- |
| krishi_salah | human_review |
| fintech_sahayak | human_review |
| pacs_kcc_docs | human_review |
| grievance_escalation | human_review |
| vermicompost_ops | human_review |
| khet_se_baat_content | human_review |
| legal_compliance_draft | human_review |
| bi_decision_support | auto |
| krishi_sos | human_review |
| satellite_crop_intel | auto |
| market_price_buyer_connect | human_review |
| market_research_demand | auto |
| customer_finder | auto |
| community_social | human_review |

`auto` still means read-only or advisory. Publishing, filing, and paying stay out of those skills.

To add another product skill, follow the project skill `add-dhara-skill`.

## Cursor project skills (agent)

These teach Cursor how to work in this repo. They do not run inside Dhara.

| Skill | When |
| --- | --- |
| `.cursor/skills/dhara-module-14/` | Any Module 14 change |
| `.cursor/skills/add-dhara-skill/` | A new folder under `skills/` |
| `.cursor/skills/add-mcp-server/` | A new folder under `mcp-servers/` |
