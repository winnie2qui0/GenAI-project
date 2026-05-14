# Procurement System API（MVP）

## 主要端點

- `POST /api/procurement/request`：建立採購需求（JSON：`{ "input_text": "..." }`；或 `multipart/form-data`：`input_text`、`input_file`）
- `GET /api/procurement/{request_id}/summary`：取得 `parsed_items`、狀態與進度（供前端重新整理）
- `POST /api/procurement/{request_id}/confirm`：確認/調整品項後啟動背景流程（爬蟲→比對→評分）
- `GET /api/procurement/{request_id}/status`：輪詢狀態
- `GET /api/procurement/{request_id}/results`：取得分群與排名結果
- `POST /api/procurement/{request_id}/decision`：寫入 `audit_log`
- `GET /api/procurement/{request_id}/export?format=pdf|excel`：匯出報表
- `GET /api/search/ping`：健康檢查

## 注意事項

- 評分為**純規則計算**（`ScoringService`），不使用 LLM。
- LLM 僅用於：需求抽取、（可選）比對裁決、結果說明。
