"""Initial schema with pgvector

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "procurement_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", sa.String(100), nullable=False),
        sa.Column("raw_input", sa.Text, nullable=False),
        sa.Column("parsed_items", JSONB, nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_procurement_user", "procurement_requests", ["user_id"])
    op.create_index("idx_procurement_status", "procurement_requests", ["status"])

    op.create_table(
        "product_clusters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("request_id", UUID(as_uuid=True), sa.ForeignKey("procurement_requests.id", ondelete="CASCADE")),
        sa.Column("canonical_name", sa.String(500), nullable=False),
        sa.Column("gtin", sa.String(50)),
        sa.Column("brand", sa.String(100)),
        sa.Column("model", sa.String(100)),
        sa.Column("confidence_level", sa.String(20), nullable=False),
        sa.Column("matching_method", sa.String(50)),
        sa.Column("specs", JSONB),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_cluster_request", "product_clusters", ["request_id"])
    op.create_index("idx_cluster_gtin", "product_clusters", ["gtin"])

    op.create_table(
        "listings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("cluster_id", UUID(as_uuid=True), sa.ForeignKey("product_clusters.id", ondelete="CASCADE")),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(100)),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False),
        sa.Column("price_normalized_usd", sa.Numeric(10, 2)),
        sa.Column("moq", sa.Integer, server_default="1"),
        sa.Column("in_stock", sa.Boolean, server_default="true"),
        sa.Column("lead_time_days", sa.Integer),
        sa.Column("rating", sa.Numeric(2, 1)),
        sa.Column("review_count", sa.Integer),
        sa.Column("seller_name", sa.String(200)),
        sa.Column("seller_rating", sa.Numeric(2, 1)),
        sa.Column("raw_data", JSONB),
        sa.Column("crawl_time", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("cache_expires_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_listing_cluster", "listings", ["cluster_id"])
    op.create_index("idx_listing_source", "listings", ["source"])
    op.create_index("idx_listing_cache", "listings", ["cache_expires_at"])

    op.create_table(
        "embeddings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("listing_id", UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE")),
        sa.Column("vector", sa.Text),  # Stored as text; pgvector type applied via raw SQL
        sa.Column("model_name", sa.String(100)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "scoring_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("request_id", UUID(as_uuid=True), sa.ForeignKey("procurement_requests.id", ondelete="CASCADE")),
        sa.Column("cluster_id", UUID(as_uuid=True), sa.ForeignKey("product_clusters.id", ondelete="CASCADE")),
        sa.Column("listing_id", UUID(as_uuid=True), sa.ForeignKey("listings.id", ondelete="CASCADE")),
        sa.Column("price_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("delivery_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("rating_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("trust_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("final_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("rank", sa.Integer, nullable=False),
        sa.Column("anomalies", JSONB, server_default="[]"),
        sa.Column("llm_explanation", sa.Text),
        sa.Column("weights_used", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_scoring_request", "scoring_results", ["request_id"])
    op.create_index("idx_scoring_rank", "scoring_results", ["request_id", "rank"])

    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("request_id", UUID(as_uuid=True), sa.ForeignKey("procurement_requests.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.String(100), nullable=False),
        sa.Column("system_recommended_listing_id", UUID(as_uuid=True), sa.ForeignKey("listings.id")),
        sa.Column("system_recommended_rank", sa.Integer),
        sa.Column("system_recommended_score", sa.Numeric(5, 2)),
        sa.Column("user_action", sa.String(50), nullable=False),
        sa.Column("user_chosen_listing_id", UUID(as_uuid=True), sa.ForeignKey("listings.id")),
        sa.Column("user_chosen_rank", sa.Integer),
        sa.Column("override_reason", sa.Text),
        sa.Column("score_snapshot", JSONB, nullable=False),
        sa.Column("anomaly_flags", JSONB),
        sa.Column("actual_delivery_date", sa.Date),
        sa.Column("actual_price", sa.Numeric(10, 2)),
        sa.Column("quality_rating", sa.Integer),
        sa.Column("feedback_notes", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_audit_request", "audit_log", ["request_id"])
    op.create_index("idx_audit_user", "audit_log", ["user_id"])
    op.create_index("idx_audit_created", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("scoring_results")
    op.drop_table("embeddings")
    op.drop_table("listings")
    op.drop_table("product_clusters")
    op.drop_table("procurement_requests")
