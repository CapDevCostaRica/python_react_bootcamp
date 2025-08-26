"""Add monster cache tables for randymorales proxy

Revision ID: randymorales_monster_cache
Revises: aa75144a150e
Create Date: 2025-08-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'randymorales_monster_cache'
down_revision: Union[str, Sequence[str], None] = 'aa75144a150e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'randymorales_monster_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('monster_index', sa.String(), unique=True, nullable=False),
        sa.Column('monster_data', sa.String(), nullable=False)
    )
    op.create_table(
        'randymorales_monster_list_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('resource', sa.String(), unique=True, nullable=False),
        sa.Column('list_data', sa.String(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('randymorales_monster_list_cache')
    op.drop_table('randymorales_monster_cache')
