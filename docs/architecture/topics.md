# Redpanda topics

Schema changes use the same review as any other interface. Payloads are JSON or Avro in Redpanda's schema registry. Producers cannot publish a shape consumers were not built for.

| Topic | Key | Value fields | Partitions | Retention | Path |
| --- | --- | --- | --- | --- | --- |
| `sos.alerts` | `plot_id` | category, severity, channel, tenant_id, created_at | 6 | 30 days | Krishi SOS → orchestrator notifier, BI |
| `satellite.ndvi.updates` | `plot_id` | ndvi, ndmi, image_date, source, confidence | 6 | 90 days | Satellite job → crop intelligence, RAG indexer |
| `mandi.price.updates` | `commodity+mandi_name` | min_price, max_price, modal_price, price_date, source | 3 | 180 days | Price puller → buyer connect, market research |
| `csp.transactions` | `tenant_id` | txn_type, amount, status, timestamp (PII already removed) | 12 | 400 days | Fintech connector → Fintech Sahayak, BI, fraud signals |

Status: OPEN. Topic folders under `streaming/topics/` hold the contract. No cluster is running.
