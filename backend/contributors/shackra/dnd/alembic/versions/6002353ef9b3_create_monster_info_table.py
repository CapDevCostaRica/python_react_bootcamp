"""Create monster info table

Revision ID: 6002353ef9b3
Revises: 
Create Date: 2025-10-20 19:07:47.336237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6002353ef9b3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "monster",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("index", sa.Integer, unique=True, nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("monster")
