import uuid
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.procurement_request import ProcurementRequest
from app.models.scoring_result import ScoringResult
from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)
router = APIRouter()
audit_service = AuditService()


@router.post("/{request_id}/decision", response_model=DecisionResponse)
async def record_decision(
    request_id: uuid.UUID,
    body: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProcurementRequest).where(ProcurementRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Build score snapshot for audit
    score_results = await db.execute(
        select(ScoringResult).where(ScoringResult.request_id == request_id).order_by(ScoringResult.rank)
    )
    scores = score_results.scalars().all()
    score_snapshot: list[dict[str, Any]] = [
        {
            "listing_id": str(s.listing_id),
            "rank": s.rank,
            "final_score": float(s.final_score),
            "price_score": float(s.price_score),
            "delivery_score": float(s.delivery_score),
            "rating_score": float(s.rating_score),
            "trust_score": float(s.trust_score),
            "weights_used": s.weights_used,
        }
        for s in scores
    ]

    audit = await audit_service.record_decision(
        db=db,
        request_id=request_id,
        user_id=req.user_id,
        action=body.action,
        chosen_listing_id=body.chosen_listing_id,
        override_reason=body.override_reason,
        score_snapshot={"scores": score_snapshot},
    )

    return DecisionResponse(audit_id=audit.id, message="Decision recorded")
