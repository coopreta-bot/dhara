# Technology stack

These are the choices to build, not a menu. Nothing in the request path is a paid third-party AI API.

| Layer | Choice |
| --- | --- |
| Server OS | Ubuntu 24.04 LTS |
| Core language | Python 3.11 |
| API | FastAPI |
| Maker/Checker dashboard | React 18, TypeScript, Next.js 14, Tailwind CSS |
| Android offline | Kotlin, Jetpack Compose, llama.cpp JNI |
| Database | PostgreSQL 16 + pgvector |
| Cache, sessions, job broker | Redis 7 |
| Event streaming | Redpanda |
| Background jobs | Celery, Celery Beat, Redis |
| RAG library | LlamaIndex, self-hosted |
| Embeddings | Self-hosted multilingual encoder (BAAI/bge-m3 class) via sentence-transformers |
| Inference | vLLM, OpenAI-compatible API bound to Coopreta's network only |
| Fine-tuning | Axolotl or LLaMA-Factory |
| Containers | Docker Compose in dev; Kubernetes or k3s in staging and production |
| CI | GitHub Actions (dev tooling, not a model dependency) |
| Secrets | HashiCorp Vault. Nothing secret is committed. |
| Observability | Prometheus, Grafana, Loki |
| Tool calling | Model Context Protocol, official Python SDK, self-hosted servers |

CI lint is Ruff and `black --check`, then pytest, then Trivy. A model-affecting change also runs Dhara-Bench before merge. Production promotion is manual and requires the 45-point checklist to be PASS or LIVE VERIFIED for every capability the change touches.
