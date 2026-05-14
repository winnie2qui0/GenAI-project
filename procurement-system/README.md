# AI-Assisted Procurement System（MVP）

此目錄包含規格中的 **Path A（標準品）** 全端 MVP：

- `backend/`：FastAPI + SQLAlchemy + Alembic（PostgreSQL / pgvector）
- `frontend/`：React + TypeScript + Vite
- `docs/`：API / DB / Prompts / 部署說明

## 快速開始（本機）

### 1) 資料庫

```bash
cd procurement-system/backend
docker compose up -d postgres
cp .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 2) 前端

```bash
cd procurement-system/frontend
npm install
npm run dev
```

### 3) 測試

```bash
cd procurement-system/backend
source .venv/bin/activate
PYTHONPATH=. pytest -q
```

## 重要設計

- **評分可重現**：`ScoringService` 不使用 LLM、不使用隨機性；同輸入同輸出。
- **爬蟲**：Amazon 嘗試解析，失敗則回退 demo listing；Alibaba / PChome / Local B2B 先以可重現的 demo 資料為主，方便端對端驗收。
