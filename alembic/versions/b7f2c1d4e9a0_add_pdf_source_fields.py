"""add pdf source fields to decks

Revision ID: b7f2c1d4e9a0
Revises: 8f4c9e2b1a3d
Create Date: 2026-05-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7f2c1d4e9a0"
down_revision = "8f4c9e2b1a3d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("decks", sa.Column("source_type", sa.String(length=32), nullable=True))
    op.add_column("decks", sa.Column("source_file", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("decks", "source_file")
    op.drop_column("decks", "source_type")
