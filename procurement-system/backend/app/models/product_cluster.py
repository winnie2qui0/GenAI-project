from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductCluster(Base):
    __tablename__ = "product_clusters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False
    )
    canonical_name: Mapped[str] = mapped_column(String(500), nullable=False)
    gtin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False)
    matching_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    specs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped["ProcurementRequest"] = relationship("ProcurementRequest", back_populates="clusters")
    listings: Mapped[list["Listing"]] = relationship(
        "Listing", back_populates="cluster", cascade="all, delete-orphan"
    )
    scoring_results: Mapped[list["ScoringResult"]] = relationship(
        "ScoringResult", back_populates="cluster", cascade="all, delete-orphan"
    )
