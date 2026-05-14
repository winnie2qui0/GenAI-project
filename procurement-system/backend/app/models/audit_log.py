from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)

    system_recommended_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True
    )
    system_recommended_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    system_recommended_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    user_action: Mapped[str] = mapped_column(String(50), nullable=False)
    user_chosen_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id"), nullable=True
    )
    user_chosen_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    score_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    anomaly_flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    actual_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    quality_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    request: Mapped["ProcurementRequest"] = relationship("ProcurementRequest", back_populates="audit_logs")
