import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ProcurementRequest, ScoringResult
from app.schemas.request import DecisionBody
from app.schemas.response import DecisionResponse
from app.services.audit_service import AuditService


router = APIRouter(tags=["decision"])


@router.post("/{request_id}/decision", response_model=DecisionResponse)
def record_decision(request_id: str, body: DecisionBody, db: Session = Depends(get_db)) -> DecisionResponse:
    settings = get_settings()
    rid = uuid.UUID(request_id)
    req = db.get(ProcurementRequest, rid)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    top = (
        db.query(ScoringResult)
        .filter(ScoringResult.request_id == rid, ScoringResult.rank == 1)
        .order_by(ScoringResult.final_score.desc())
        .first()
    )
    system_listing_id = top.listing_id if top else None
    system_rank = int(top.rank) if top else None
    system_score = Decimal(top.final_score) if top else None

    chosen_uuid = uuid.UUID(body.chosen_listing_id) if body.chosen_listing_id else None
    user_rank = None
    if chosen_uuid:
        row = (
            db.query(ScoringResult)
            .filter(ScoringResult.request_id == rid, ScoringResult.listing_id == chosen_uuid)
            .first()
        )
        user_rank = int(row.rank) if row else None

    scores = db.query(ScoringResult).filter(ScoringResult.request_id == rid).all()
    snapshot = {
        str(s.listing_id): {
            "rank": int(s.rank),
            "final_score": float(s.final_score),
            "price_score": float(s.price_score),
            "delivery_score": float(s.delivery_score),
            "rating_score": float(s.rating_score),
            "trust_score": float(s.trust_score),
        }
        for s in scores
    }

    anomalies: list = []
    if chosen_uuid:
        row = (
            db.query(ScoringResult)
            .filter(ScoringResult.request_id == rid, ScoringResult.listing_id == chosen_uuid)
            .first()
        )
        if row and row.anomalies:
            anomalies = list(row.anomalies)

    audit = AuditService()
    log = audit.record_decision(
        db,
        request_id=rid,
        user_id=settings.demo_user_id,
        action=body.action,
        chosen_listing_id=chosen_uuid,
        override_reason=body.override_reason,
        system_recommended_listing_id=system_listing_id,
        system_recommended_rank=system_rank,
        system_recommended_score=system_score,
        user_chosen_rank=user_rank,
        score_snapshot=snapshot,
        anomaly_flags=anomalies or None,
    )

    return DecisionResponse(audit_id=str(log.id))
