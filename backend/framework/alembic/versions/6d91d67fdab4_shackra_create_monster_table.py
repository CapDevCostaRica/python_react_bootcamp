"""shackra: Create monster table

Revision ID: 6d91d67fdab4
Revises: 177f6234a79f
Create Date: 2025-10-21 15:49:04.429273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d91d67fdab4'
down_revision: Union[str, Sequence[str], None] = '177f6234a79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shackra_monster",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("index", sa.Integer, unique=True, nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("shackra_monster")
