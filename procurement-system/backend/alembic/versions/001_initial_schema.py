"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-14
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

from app.database import Base

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    bind.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
