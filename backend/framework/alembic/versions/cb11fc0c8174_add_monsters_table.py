"""add monsters table

Revision ID: cb11fc0c8174
Revises: aa75144a150e
Create Date: 2025-08-25 16:41:19.945708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb11fc0c8174'
down_revision: Union[str, Sequence[str], None] = 'aa75144a150e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('wainermora_monsters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('index', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('subtype', sa.String(), nullable=True),
        sa.Column('alignment', sa.String(), nullable=True),
        sa.Column('armor_class', sa.JSON(), nullable=True),
        sa.Column('hit_points', sa.Integer(), nullable=True),
        sa.Column('hit_dice', sa.String(), nullable=True),
        sa.Column('hit_points_roll', sa.String(), nullable=True),
        sa.Column('speed', sa.JSON(), nullable=True),
        sa.Column('strength', sa.Integer(), nullable=True),
        sa.Column('dexterity', sa.Integer(), nullable=True),
        sa.Column('constitution', sa.Integer(), nullable=True),
        sa.Column('intelligence', sa.Integer(), nullable=True),
        sa.Column('wisdom', sa.Integer(), nullable=True),
        sa.Column('charisma', sa.Integer(), nullable=True),
        sa.Column('proficiencies', sa.JSON(), nullable=True),
        sa.Column('damage_vulnerabilities', sa.JSON(), nullable=True),
        sa.Column('damage_resistances', sa.JSON(), nullable=True),
        sa.Column('damage_immunities', sa.JSON(), nullable=True),
        sa.Column('condition_immunities', sa.JSON(), nullable=True),
        sa.Column('senses', sa.JSON(), nullable=True),
        sa.Column('languages', sa.String(), nullable=True),
        sa.Column('challenge_rating', sa.Float(), nullable=True),
        sa.Column('proficiency_bonus', sa.Integer(), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('special_abilities', sa.JSON(), nullable=True),
        sa.Column('actions', sa.JSON(), nullable=True),
        sa.Column('legendary_actions', sa.JSON(), nullable=True),
        sa.Column('reactions', sa.JSON(), nullable=True),
        sa.Column('forms', sa.JSON(), nullable=True),
        sa.Column('spellcasting', sa.JSON(), nullable=True),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('index')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('wainermora_monsters')
