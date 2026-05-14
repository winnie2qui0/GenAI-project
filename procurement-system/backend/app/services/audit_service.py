from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditService:
    def record_decision(
        self,
        db: Session,
        *,
        request_id: uuid.UUID,
        user_id: str,
        action: str,
        chosen_listing_id: uuid.UUID | None,
        override_reason: str | None,
        system_recommended_listing_id: uuid.UUID | None,
        system_recommended_rank: int | None,
        system_recommended_score: Decimal | None,
        user_chosen_rank: int | None,
        score_snapshot: dict[str, Any],
        anomaly_flags: list[dict[str, Any]] | None,
    ) -> AuditLog:
        row = AuditLog(
            request_id=request_id,
            user_id=user_id,
            user_action=action,
            user_chosen_listing_id=chosen_listing_id,
            override_reason=override_reason,
            system_recommended_listing_id=system_recommended_listing_id,
            system_recommended_rank=system_recommended_rank,
            system_recommended_score=system_recommended_score,
            user_chosen_rank=user_chosen_rank,
            score_snapshot=score_snapshot,
            anomaly_flags=anomaly_flags,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row
