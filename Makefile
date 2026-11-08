.PHONY: dev lint test eval

dev:
	@echo "OPEN: use infra/docker-compose.pgvector.yml for local Postgres + pgvector; the RAG query service remains unimplemented."
	@exit 1

lint:
	ruff check .
	black --check .

test:
	pytest

eval:
	@echo "OPEN: Dhara-Bench is not implemented. See models/eval/README.md"
	@exit 1
