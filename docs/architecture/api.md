# HTTP API

FastAPI publishes OpenAPI at `/openapi.json` for the implemented API
foundation. This table remains the contract for the API as a whole. Status:
OPEN.

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/query` | JWT | Grounded RAG answer plus citations |
| POST | `/skills/{skill_name}/invoke` | JWT and ABAC tenant check | Dispatch to a Dhara Skill |
| POST | `/sos/alert` | JWT or channel webhook signature | Raise a Krishi SOS alert |
| GET | `/satellite/ndvi/{plot_id}` | JWT | Latest NDVI/NDMI for a plot |
| GET | `/mandi/prices` | JWT | Current mandi snapshot |
| GET | `/buyers/match` | JWT | Ranked buyer leads |
| GET | `/admin/maker-checker` | JWT, reviewer role | Pending human-review items |
| POST | `/admin/maker-checker/{id}/approve` | JWT, reviewer role | Approve a queued action |
| POST | `/admin/maker-checker/{id}/reject` | JWT, reviewer role | Reject a queued action |
| GET | `/health` | none | Liveness and readiness |
| GET | `/metrics` | internal only | Prometheus scrape |

Currently, only `GET /health` is implemented in `rag/app.py`. It runs a
database `SELECT 1` readiness check and returns HTTP 200 only when it passes;
the RAG endpoint and every authenticated endpoint remain OPEN.

Human JWTs expire in 15 minutes. Refresh tokens expire in 7 days. Service-to-service calls use mutual TLS, not bearer tokens.

## Jobs

Celery Beat on Redis:

| Job | Cadence | Does |
| --- | --- | --- |
| `pull_satellite_imagery` | weekly | Sentinel-2 or Bhuvan pull, NDVI/NDMI per plot |
| `pull_mandi_prices` | daily | eNAM or Agmarknet ingestion |
| `reindex_rag_corpus` | nightly | Re-embed documents changed that day |
| `run_dhara_bench` | every model promotion | Eval gate. Failure blocks promotion |
| `expire_maker_checker_queue` | hourly | Flag reviews past SLA |
| `rotate_vault_db_credentials` | every 24h | Rotate short-lived database credentials |
