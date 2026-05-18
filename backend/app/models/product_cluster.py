import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class ProductCluster(Base):
    __tablename__ = "product_clusters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"))
    canonical_name: Mapped[str] = mapped_column(String(500), nullable=False)
    gtin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False)
    matching_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    specs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    listings: Mapped[list] = relationship("Listing", back_populates="cluster", cascade="all, delete-orphan")
