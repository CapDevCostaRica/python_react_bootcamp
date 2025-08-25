"""luch1f3rchocr: create monster cache table

Revision ID: 037310dbed06
Revises: aa75144a150e
Create Date: 2025-08-25 04:09:16.793078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '037310dbed06'
down_revision: Union[str, Sequence[str], None] = 'aa75144a150e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "monster_cache",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("cached_at", sa.DateTime(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("monster_cache")
