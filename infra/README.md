# infra

Isolated VPC, GPU nodes, and private subnets. Do not provision into the current AWS account until the P0 security HOLD is cleared.

`docker-compose.pgvector.yml` is IMPLEMENTED for a loopback-only local
Postgres 16 + pgvector development service. It is not AWS infrastructure and
does not bypass the AWS foundation SECURITY GATE BLOCKED hold. The service
requires a local secret file at `infra/.env.pgvector`, which is ignored by Git.

For a low-capacity workstation, `.github/workflows/pgvector-integration.yml`
provides the preferred remote verification path with generated data only.
Docker was not available on the development host when this configuration was
added, so the local service has not been started or independently verified.
