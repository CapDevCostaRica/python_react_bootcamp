"""Create people tables

Revision ID: 241c8360cde5
Revises: 
Create Date: 2025-08-29 00:04:36.820218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '241c8360cde5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('family',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=True),
        sa.Column('kinship', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('favorite_food',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=True),
        sa.Column('food', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hobbies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=True),
        sa.Column('hobby', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('people',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('eye_color', sa.String(), nullable=True),
        sa.Column('hair_color', sa.String(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('height_cm', sa.Integer(), nullable=True),
        sa.Column('weight_kg', sa.Integer(), nullable=True),
        sa.Column('nationality', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('studies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person_id', sa.Integer(), nullable=True),
        sa.Column('degree', sa.String(), nullable=True),
        sa.Column('institution', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('family')
    op.drop_table('favorite_food')
    op.drop_table('hobbies')
    op.drop_table('people')
    op.drop_table('studies')
