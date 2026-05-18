import asyncio
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.procurement_request import ProcurementRequest
from app.models.product_cluster import ProductCluster
from app.models.listing import Listing
from app.models.scoring_result import ScoringResult
from app.schemas.request import ProcurementRequestCreate, ProcurementConfirm
from app.schemas.response import (
    ProcurementRequestResponse,
    StatusResponse,
    ResultsResponse,
    ClusterResult,
    RankedListing,
    ScoreBreakdown,
    AnomalyFlag,
)
from app.services.llm_service import LLMService
from app.services.crawler_service import CrawlerService, get_status

logger = logging.getLogger(__name__)
router = APIRouter()

llm_service = LLMService()
crawler_service = CrawlerService()


@router.post("/request", status_code=201, response_model=ProcurementRequestResponse)
async def create_request(
    input_text: str = Form(""),
    user_id: str = Form("demo_user"),
    file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
):
    raw_input = input_text
    if file:
        content = await file.read()
        raw_input += f"\n[Uploaded file: {file.filename}]"

    if not raw_input.strip():
        raise HTTPException(status_code=422, detail="Provide input_text or upload a file")

    extraction = await llm_service.extract_requirements(raw_input)

    req = ProcurementRequest(
        user_id=user_id,
        raw_input=raw_input,
        parsed_items=[item.model_dump() for item in extraction.items],
        status="pending",
    )
    db.add(req)
    await db.flush()

    return ProcurementRequestResponse(
        request_id=req.id,
        parsed_items=req.parsed_items,
        status=req.status,
        created_at=req.created_at,
    )


@router.post("/{request_id}/confirm")
async def confirm_request(
    request_id: uuid.UUID,
    body: ProcurementConfirm,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProcurementRequest).where(ProcurementRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.parsed_items = [item.model_dump() for item in body.items]
    req.status = "processing"
    await db.flush()

    items_dicts = req.parsed_items

    async def run_bg():
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as bg_db:
            await crawler_service.run_pipeline(bg_db, request_id, items_dicts)

    asyncio.create_task(run_bg())

    return {"message": "Processing started", "request_id": str(request_id)}


@router.get("/{request_id}/status", response_model=StatusResponse)
async def get_request_status(request_id: uuid.UUID):
    status_data = get_status(str(request_id))
    return StatusResponse(
        status=status_data.get("status", "pending"),
        progress=status_data.get("progress", {}),
    )


@router.get("/{request_id}/results", response_model=ResultsResponse)
async def get_results(request_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProcurementRequest).where(ProcurementRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status not in ("completed",):
        raise HTTPException(status_code=202, detail=f"Processing not complete: {req.status}")

    cluster_result = await db.execute(
        select(ProductCluster).where(ProductCluster.request_id == request_id)
    )
    clusters = cluster_result.scalars().all()

    cluster_responses = []
    for cluster in clusters:
        score_result = await db.execute(
            select(ScoringResult, Listing)
            .join(Listing, ScoringResult.listing_id == Listing.id)
            .where(ScoringResult.cluster_id == cluster.id)
            .order_by(ScoringResult.rank)
        )
        rows = score_result.all()

        ranked_listings = []
        for sr, listing in rows:
            ranked_listings.append(
                RankedListing(
                    rank=sr.rank,
                    listing_id=listing.id,
                    source=listing.source,
                    title=listing.title,
                    price=float(listing.price),
                    currency=listing.currency,
                    price_usd=float(listing.price_normalized_usd) if listing.price_normalized_usd else None,
                    delivery_days=listing.lead_time_days,
                    rating=float(listing.rating) if listing.rating else None,
                    review_count=listing.review_count,
                    moq=listing.moq,
                    seller_name=listing.seller_name,
                    final_score=float(sr.final_score),
                    score_breakdown=ScoreBreakdown(
                        price_score=float(sr.price_score),
                        delivery_score=float(sr.delivery_score),
                        rating_score=float(sr.rating_score),
                        trust_score=float(sr.trust_score),
                    ),
                    anomalies=[AnomalyFlag(**a) for a in (sr.anomalies or [])],
                    llm_explanation=sr.llm_explanation,
                    url=listing.url,
                )
            )

        cluster_responses.append(
            ClusterResult(
                cluster_id=cluster.id,
                canonical_name=cluster.canonical_name,
                confidence=cluster.confidence_level,
                matching_method=cluster.matching_method,
                ranked_listings=ranked_listings,
            )
        )

    return ResultsResponse(request_id=request_id, clusters=cluster_responses)
