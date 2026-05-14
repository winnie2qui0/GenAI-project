import io
import uuid
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Listing, ProcurementRequest, ProductCluster, ScoringResult
from app.schemas.request import ConfirmProcurementBody, CreateProcurementBody
from app.schemas.response import (
    ClusterResult,
    CrawlProgress,
    ListingRanked,
    ProcurementResultsResponse,
    ProcurementStatusResponse,
    RequestCreatedResponse,
    ScoreBreakdown,
)
from app.services.llm_service import LLMService
from app.services.procurement_pipeline import run_procurement_pipeline


router = APIRouter(tags=["procurement"])


async def _file_to_text(upload) -> str:
    data = await upload.read()
    buf = io.BytesIO(data)
    name = (getattr(upload, "filename", "") or "").lower()
    if name.endswith(".csv"):
        df = pd.read_csv(buf)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(buf)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type; use .csv or .xlsx")
    return df.head(500).to_csv(index=False)


@router.post("/request", response_model=RequestCreatedResponse, status_code=201)
async def create_procurement_request(
    request: Request,
    db: Session = Depends(get_db),
) -> RequestCreatedResponse:
    settings = get_settings()
    raw_parts: list[str] = []
    ct = request.headers.get("content-type", "")

    if "application/json" in ct:
        payload = await request.json()
        body = CreateProcurementBody.model_validate(payload)
        if body.input_text:
            raw_parts.append(body.input_text.strip())
    else:
        form = await request.form()
        txt = str(form.get("input_text") or "").strip()
        if txt:
            raw_parts.append(txt)
        up = form.get("input_file")
        if up is not None and hasattr(up, "read"):
            raw_parts.append(await _file_to_text(up))

    raw = "\n".join(p for p in raw_parts if p).strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Provide input_text and/or input_file")

    llm = LLMService()
    extracted = await llm.extract_requirements(raw)
    if "items" not in extracted or not extracted["items"]:
        raise HTTPException(status_code=400, detail="LLM extraction produced no items")

    row = ProcurementRequest(
        user_id=settings.demo_user_id,
        raw_input=raw,
        parsed_items=extracted,
        status="pending",
        progress=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return RequestCreatedResponse(
        request_id=str(row.id),
        parsed_items=extracted.get("items", []),
        status=row.status,
    )


@router.post("/{request_id}/confirm")
async def confirm_procurement(
    request_id: str,
    payload: ConfirmProcurementBody,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    rid = uuid.UUID(request_id)
    row = db.get(ProcurementRequest, rid)
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")

    parsed = row.parsed_items
    if not isinstance(parsed, dict):
        parsed = {"items": parsed, "missing_info": [], "confidence": "medium"}
    parsed["items"] = [i.model_dump() for i in payload.items]
    row.parsed_items = parsed
    row.status = "crawling"
    row.updated_at = datetime.utcnow()
    db.commit()

    background_tasks.add_task(run_procurement_pipeline, request_id)
    return {"ok": True, "status": "crawling"}


@router.get("/{request_id}/summary", response_model=dict)
def get_procurement_request(request_id: str, db: Session = Depends(get_db)) -> dict:
    rid = uuid.UUID(request_id)
    row = db.get(ProcurementRequest, rid)
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "request_id": str(row.id),
        "status": row.status,
        "parsed_items": row.parsed_items,
        "progress": row.progress,
    }


@router.get("/{request_id}/status", response_model=ProcurementStatusResponse)
def procurement_status(request_id: str, db: Session = Depends(get_db)) -> ProcurementStatusResponse:
    rid = uuid.UUID(request_id)
    row = db.get(ProcurementRequest, rid)
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    prog = row.progress or {}
    return ProcurementStatusResponse(
        status=row.status,
        progress=CrawlProgress(
            platforms_crawled=int(prog.get("platforms_crawled", 0)),
            total_platforms=int(prog.get("total_platforms", 4)),
            listings_found=int(prog.get("listings_found", 0)),
            clusters_created=int(prog.get("clusters_created", 0)),
        ),
    )


@router.get("/{request_id}/results", response_model=ProcurementResultsResponse)
def procurement_results(request_id: str, db: Session = Depends(get_db)) -> ProcurementResultsResponse:
    rid = uuid.UUID(request_id)
    row = db.get(ProcurementRequest, rid)
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")

    clusters = db.query(ProductCluster).filter(ProductCluster.request_id == rid).all()
    out_clusters: list[ClusterResult] = []
    for c in clusters:
        scores = (
            db.query(ScoringResult)
            .filter(ScoringResult.cluster_id == c.id)
            .order_by(ScoringResult.rank.asc())
            .all()
        )
        ranked: list[ListingRanked] = []
        for s in scores:
            lst = db.get(Listing, s.listing_id)
            if not lst:
                continue
            ranked.append(
                ListingRanked(
                    rank=int(s.rank),
                    listing_id=str(lst.id),
                    source=lst.source,
                    price=float(lst.price),
                    currency=lst.currency,
                    price_usd=float(lst.price_normalized_usd) if lst.price_normalized_usd is not None else None,
                    delivery_days=lst.lead_time_days,
                    rating=float(lst.rating) if lst.rating is not None else None,
                    final_score=float(s.final_score),
                    score_breakdown=ScoreBreakdown(
                        price_score=float(s.price_score),
                        delivery_score=float(s.delivery_score),
                        rating_score=float(s.rating_score),
                        trust_score=float(s.trust_score),
                    ),
                    anomalies=list(s.anomalies or []),
                    llm_explanation=s.llm_explanation,
                    url=lst.url,
                )
            )
        out_clusters.append(
            ClusterResult(
                cluster_id=str(c.id),
                canonical_name=c.canonical_name,
                confidence=c.confidence_level,
                ranked_listings=ranked,
            )
        )

    return ProcurementResultsResponse(request_id=request_id, clusters=out_clusters)
