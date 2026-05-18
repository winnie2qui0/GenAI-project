from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db
from app.api import procurement, decision, report

settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up procurement system...")
    await init_db()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AI-Assisted Procurement System",
    description="Automate price comparison for standard office products",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(procurement.router, prefix="/api/procurement", tags=["procurement"])
app.include_router(decision.router, prefix="/api/procurement", tags=["decision"])
app.include_router(report.router, prefix="/api/procurement", tags=["report"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
