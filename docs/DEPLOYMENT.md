# Deployment Guide

## Local Development (Recommended for MVP)

```bash
# 1. Start PostgreSQL
cd procurement-system
docker-compose up -d postgres

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in API keys
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev            # http://localhost:5173
```

## Full Stack (Docker Compose)

```bash
cd procurement-system
cp backend/.env.example .env
# Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env
docker-compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key |
| `ANTHROPIC_API_KEY` | If using Anthropic | Anthropic API key |
| `LLM_PROVIDER` | No | `openai` (default) or `anthropic` |
| `LLM_MODEL` | No | Model name |
| `SCORING_WEIGHT_*` | No | Override scoring weights |

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```
