"""create andresnboza first table

Revision ID: 2d90d3da552a
Revises: aa75144a150e
Create Date: 2025-08-25 22:51:19.387983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d90d3da552a'
down_revision: Union[str, Sequence[str], None] = 'aa75144a150e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'andresnboza_monster',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('andresnboza_monster')
