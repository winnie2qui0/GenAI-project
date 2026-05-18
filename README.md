# AI-Assisted Procurement System — MVP

Automates price comparison for standard office products by crawling multiple B2B/e-commerce platforms, matching identical products across sources, and recommending the best supplier using a deterministic scoring algorithm.

## Architecture

```
User Input → LLM Extraction → Parameter Confirmation
    → Parallel Crawl (Amazon, Alibaba, PChome, Local B2B)
    → 3-Layer Product Matching (GTIN → Brand+Model → Embedding+LLM)
    → Anomaly Detection
    → Deterministic Scoring
    → LLM Explanation
    → User Decision → Audit Log
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI + SQLAlchemy (async) |
| Database | PostgreSQL 16 + pgvector |
| LLM | OpenAI GPT-4 or Anthropic Claude |
| Crawlers | httpx + BeautifulSoup4 |
| Reports | ReportLab (PDF) + XlsxWriter (Excel) |

## Quick Start

```bash
# Prerequisites: Docker, Python 3.11+, Node 20+

cd procurement-system

# Start database
docker-compose up -d postgres

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your LLM API key
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install && npm run dev
```

Open http://localhost:5173

## Scoring Algorithm

Scores are **100% deterministic** — no LLM, no randomness:

| Dimension | Weight | Method |
|---|---|---|
| Price | 30% | Min-Max normalization within cluster |
| Delivery | 30% | 100 if within limit; -10pts/day over |
| Rating | 20% | Star × 20, weighted by review count |
| Trust | 20% | Fixed score per platform |

## LLM Usage (3 calls only)

1. **Requirement extraction** — parse natural language → structured JSON
2. **Product matching judgment** — confirm ambiguous matches (Layer 3 only)
3. **Recommendation explanation** — generate markdown analysis after scoring

LLM does **not** influence scores or rankings.

## Project Structure

```
procurement-system/
├── backend/          FastAPI app, services, crawlers, models
├── frontend/         React + TypeScript UI
├── docs/             API, database, prompts, deployment docs
└── docker-compose.yml
```

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Documentation

- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [LLM Prompts](docs/PROMPTS.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
