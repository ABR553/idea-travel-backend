"""add_link_clicks_table

Revision ID: c0808c8ff02a
Revises: 003
Create Date: 2026-03-21 20:45:11.390398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c0808c8ff02a'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'link_clicks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.String(20), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('clicked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(
        'ix_link_clicks_entity_clicked_at',
        'link_clicks',
        ['entity_type', 'entity_id', 'clicked_at'],
    )


def downgrade() -> None:
    op.drop_index('ix_link_clicks_entity_clicked_at', table_name='link_clicks')
    op.drop_table('link_clicks')
