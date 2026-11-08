# Upstream repositories

Shallow clones live in `third_party/` (gitignored). They are reference source for the stack in `docs/architecture/stack.md`. Dhara still does not call a third-party inference API.

| Folder | Repository |
| --- | --- |
| `fastapi` | https://github.com/fastapi/fastapi |
| `next.js` | https://github.com/vercel/next.js |
| `llama.cpp` | https://github.com/ggml-org/llama.cpp |
| `pgvector` | https://github.com/pgvector/pgvector |
| `redpanda` | https://github.com/redpanda-data/redpanda |
| `celery` | https://github.com/celery/celery |
| `llama_index` | https://github.com/run-llama/llama_index |
| `sentence-transformers` | https://github.com/UKPLab/sentence-transformers |
| `vllm` | https://github.com/vllm-project/vllm |
| `axolotl` | https://github.com/axolotl-ai-cloud/axolotl |
| `LLaMA-Factory` | https://github.com/hiyouga/LLaMA-Factory |
| `vault` | https://github.com/hashicorp/vault |
| `prometheus` | https://github.com/prometheus/prometheus |
| `grafana` | https://github.com/grafana/grafana |
| `python-sdk` | https://github.com/modelcontextprotocol/python-sdk |
| `servers` | https://github.com/modelcontextprotocol/servers |

Python packages installed into `.venv` from PyPI, not from these clones: `mcp`, `fastapi`, `uvicorn`, `pydantic`, `pyyaml`, `black`, `ruff`, `pytest`, `pre-commit`. vLLM, Axolotl, and sentence-transformers are not pip-installed here: they need a Linux GPU box, and this machine is Windows.
