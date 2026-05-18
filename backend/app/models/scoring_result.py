import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Numeric, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ScoringResult(Base):
    __tablename__ = "scoring_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"))
    cluster_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_clusters.id", ondelete="CASCADE"))
    listing_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"))

    price_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    delivery_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    rating_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    trust_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    anomalies: Mapped[list] = mapped_column(JSONB, default=list)
    llm_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    weights_used: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
