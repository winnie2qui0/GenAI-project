from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.decision import router as decision_router
from app.api.procurement import router as procurement_router
from app.api.report import router as report_router
from app.api.search import router as search_router


def create_app() -> FastAPI:
    app = FastAPI(title="Procurement System API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(procurement_router, prefix="/api/procurement")
    app.include_router(decision_router, prefix="/api/procurement")
    app.include_router(report_router, prefix="/api/procurement")
    app.include_router(search_router, prefix="/api/search")
    return app


app = create_app()
