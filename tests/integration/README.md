# integration

Integration tests, including orchestrator dispatch once that code exists.

`test_pgvector_stack.py` is IMPLEMENTED and skipped by default. It applies the
local pgvector migration, stages a consent-recorded public corpus, loads it,
checks the `vector` extension and inserted row, then removes its generated
tenant row.

`.github/workflows/pgvector-integration.yml` runs that test on an ephemeral
GitHub Actions Postgres + pgvector service using generated data only. It needs
no Docker Desktop or database credentials on a developer workstation.

To run it after Docker is installed:

```powershell
Copy-Item .\infra\pgvector.env.example .\infra\.env.pgvector
# Replace DHARA_POSTGRES_PASSWORD in infra/.env.pgvector.
docker compose --env-file .\infra\.env.pgvector -f .\infra\docker-compose.pgvector.yml up -d

$password = (Get-Content .\infra\.env.pgvector | Where-Object { $_ -like "DHARA_POSTGRES_PASSWORD=*" }) -replace "^DHARA_POSTGRES_PASSWORD=", ""
$env:DHARA_DATABASE_URL = "postgresql+asyncpg://dhara:$password@localhost:5432/dhara"
$env:DHARA_RUN_PGVECTOR_INTEGRATION = "1"
python -m pytest .\tests\integration\test_pgvector_stack.py -q
```

Stop the local service with `docker compose --env-file .\infra\.env.pgvector
-f .\infra\docker-compose.pgvector.yml down`. Add `-v` only when intentionally
deleting the local development database.
