"""add kevinWalshMunoz monster tables

Revision ID: b872c2842a95
Revises: aa75144a150e
Create Date: 2025-08-25 00:45:12.566339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b872c2842a95'
# Set this to the revision that comes BEFORE your first migration
down_revision: Union[str, Sequence[str], None] = 'aa75144a150e' 
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create kevinWalshMunozMonsters table with updated fields
    op.create_table('kevinWalshMunozMonsters',
        sa.Column('index', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('index')
    )
    
    # Create detailed kevinWalshMunozMonster table
    op.create_table('kevinWalshMunozMonster',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('index', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('size', sa.Text(), nullable=True),
        sa.Column('type', sa.Text(), nullable=True),
        sa.Column('alignment', sa.Text(), nullable=True),
        sa.Column('armor_class', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('hit_points', sa.Integer(), nullable=True),
        sa.Column('hit_dice', sa.Text(), nullable=True),
        sa.Column('hit_points_roll', sa.Text(), nullable=True),
        sa.Column('speed', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('strength', sa.Integer(), nullable=True),
        sa.Column('dexterity', sa.Integer(), nullable=True),
        sa.Column('constitution', sa.Integer(), nullable=True),
        sa.Column('intelligence', sa.Integer(), nullable=True),
        sa.Column('wisdom', sa.Integer(), nullable=True),
        sa.Column('charisma', sa.Integer(), nullable=True),
        sa.Column('proficiencies', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_vulnerabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_resistances', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_immunities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('condition_immunities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('senses', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('languages', sa.Text(), nullable=True),
        sa.Column('challenge_rating', sa.Integer(), nullable=True),
        sa.Column('proficiency_bonus', sa.Integer(), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('special_abilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('legendary_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reactions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('forms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('index')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop both tables
    op.drop_table('kevinWalshMunozMonster')
    op.drop_table('kevinWalshMunozMonsters')