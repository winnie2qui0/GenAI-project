# Database Schema

**Engine:** PostgreSQL 16 with `pgvector` extension

**Single-DB approach:** PostgreSQL handles relational data, vector embeddings (pgvector), and TTL-based caching via `cache_expires_at` timestamp columns.

## Tables

| Table | Purpose |
|---|---|
| `procurement_requests` | User's procurement request + LLM-parsed items |
| `product_clusters` | Groups of listings identified as the same product |
| `listings` | Individual listings crawled from platforms |
| `embeddings` | Vector embeddings for product matching (384-dim) |
| `scoring_results` | Deterministic scores + rankings per listing |
| `audit_log` | Complete decision history for transparency |

## Key Design Decisions

- **No Redis:** TTL via `cache_expires_at` column in `listings` (48h default)
- **pgvector:** `ivfflat` index on 384-dimension embeddings
- **Cascade deletes:** Deleting a request removes all related data
- **JSONB:** `parsed_items`, `raw_data`, `score_snapshot` stored as JSONB for flexibility
- **Immutable audit log:** `score_snapshot` captures full weights + scores at decision time

## Migrations

```bash
cd backend
alembic upgrade head      # Apply all migrations
alembic revision --autogenerate -m "description"  # New migration
alembic downgrade -1      # Roll back one
```
