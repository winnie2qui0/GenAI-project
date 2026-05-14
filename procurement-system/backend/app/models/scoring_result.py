from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScoringResult(Base):
    __tablename__ = "scoring_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_clusters.id", ondelete="CASCADE"), nullable=False
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )

    price_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    delivery_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    rating_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    trust_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    final_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    anomalies: Mapped[list] = mapped_column(JSONB, default=list)
    llm_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    weights_used: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped["ProcurementRequest"] = relationship("ProcurementRequest", back_populates="scoring_results")
    cluster: Mapped["ProductCluster"] = relationship("ProductCluster", back_populates="scoring_results")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="scoring_results")
