import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime, Numeric, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_clusters.id", ondelete="CASCADE"))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    price_normalized_usd: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    moq: Mapped[int] = mapped_column(Integer, default=1)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Numeric(2, 1), nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seller_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    seller_rating: Mapped[float | None] = mapped_column(Numeric(2, 1), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    crawl_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    cache_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cluster: Mapped["ProductCluster"] = relationship("ProductCluster", back_populates="listings")
    embedding: Mapped["Embedding"] = relationship("Embedding", back_populates="listing", uselist=False, cascade="all, delete-orphan")
