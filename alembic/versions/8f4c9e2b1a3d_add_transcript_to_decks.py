"""add transcript to decks

Revision ID: 8f4c9e2b1a3d
Revises: 4aecbbd97834
Create Date: 2026-05-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '8f4c9e2b1a3d'
down_revision = '4aecbbd97834'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('decks', sa.Column('transcript', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('decks', 'transcript')
