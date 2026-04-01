"""add unique partial index product project external_id

Revision ID: e7f8a9b0c1d2
Revises: b30399e31d32, d1a2b3c4e5f6
Create Date: 2026-04-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, tuple, None] = ("b30399e31d32", "d1a2b3c4e5f6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_product_project_external_id",
        "products",
        ["project_id", "external_id"],
        unique=True,
        postgresql_where="project_id IS NOT NULL AND external_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_index("uq_product_project_external_id", table_name="products")
