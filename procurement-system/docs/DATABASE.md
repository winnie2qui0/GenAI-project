# Database（PostgreSQL + pgvector）

## 延伸套件

- `uuid-ossp`
- `vector`（pgvector）

## 主要資料表

- `procurement_requests`：原始輸入、`parsed_items` JSONB、`status`、`progress` JSONB
- `product_clusters`：同品群組與比對方法/信心
- `listings`：各平台刊登；`cache_expires_at` 作為快取 TTL
- `embeddings`：`vector(384)`（MVP 可不寫入，但欄位已預留）
- `scoring_results`：分項分數、排名、異常旗標、`weights_used`、`llm_explanation`
- `audit_log`：系統建議與使用者決策快照

## 遷移

在 `procurement-system/backend`：

```bash
alembic upgrade head
```
