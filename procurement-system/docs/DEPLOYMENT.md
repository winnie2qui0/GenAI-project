# Deployment（MVP）

## Docker Compose（資料庫 + 後端）

在 repo 根目錄：

```bash
docker compose up --build
```

啟動後開啟 `http://localhost:8000/docs` 檢視 OpenAPI。`backend` 服務啟動時會自動執行 `alembic upgrade head`。

## 前端

```bash
cd procurement-system/frontend
npm install
npm run dev
```

建議開發時使用 Vite proxy（已設定）或 `VITE_API_URL` 指向後端。

## 選用：向量比對模型

若要啟用 `sentence-transformers`（第三層 embedding 比對），另外安裝：

```bash
pip install -r requirements-ml.txt
```
