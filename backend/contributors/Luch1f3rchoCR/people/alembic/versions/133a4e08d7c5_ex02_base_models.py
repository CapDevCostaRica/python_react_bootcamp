"""ex02 base models

Revision ID: 133a4e08d7c5
Revises:
Create Date: 2025-08-31 11:53:49.288359
"""
from typing import Sequence, Union
from alembic import op


revision: str = "133a4e08d7c5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("DROP TABLE IF EXISTS monster_cache CASCADE;")
    op.execute("DROP TABLE IF EXISTS motivational_phrases CASCADE;")



def downgrade() -> None:

    pass