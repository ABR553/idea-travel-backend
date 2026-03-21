"""add days to destinations and nights to accommodations

Revision ID: 003
Revises: 002
Create Date: 2026-03-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("destinations", sa.Column("days", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("accommodations", sa.Column("nights", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_column("accommodations", "nights")
    op.drop_column("destinations", "days")
