import uuid
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.scoring_result import ScoringResult

logger = logging.getLogger(__name__)


class AuditService:
    async def record_decision(
        self,
        db: AsyncSession,
        request_id: uuid.UUID,
        user_id: str,
        action: str,
        chosen_listing_id: uuid.UUID | None,
        override_reason: str | None,
        score_snapshot: dict[str, Any],
    ) -> AuditLog:
        # Get top-ranked listing for system recommendation
        result = await db.execute(
            select(ScoringResult)
            .where(ScoringResult.request_id == request_id)
            .order_by(ScoringResult.rank)
            .limit(1)
        )
        top = result.scalar_one_or_none()

        # Determine user chosen rank
        user_rank = None
        if chosen_listing_id:
            rank_result = await db.execute(
                select(ScoringResult)
                .where(
                    ScoringResult.request_id == request_id,
                    ScoringResult.listing_id == chosen_listing_id,
                )
            )
            chosen_score = rank_result.scalar_one_or_none()
            if chosen_score:
                user_rank = chosen_score.rank

        audit = AuditLog(
            request_id=request_id,
            user_id=user_id,
            system_recommended_listing_id=top.listing_id if top else None,
            system_recommended_rank=top.rank if top else None,
            system_recommended_score=float(top.final_score) if top else None,
            user_action=action,
            user_chosen_listing_id=chosen_listing_id,
            user_chosen_rank=user_rank,
            override_reason=override_reason,
            score_snapshot=score_snapshot,
        )
        db.add(audit)
        await db.flush()
        return audit
