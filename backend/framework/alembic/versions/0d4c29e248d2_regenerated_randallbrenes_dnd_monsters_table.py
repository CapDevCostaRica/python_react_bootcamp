"""Created randallbrenes_dnd_monsters table

Revision ID: 0d4c29e248d2
Revises: 0d4c29e248d1
Create Date: 2025-08-25 12:23:04.461588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0d4c29e248d2'
down_revision: Union[str, Sequence[str], None] = '0d4c29e248d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Drop table if exists and recreate it with correct fields"""
    op.execute("DROP TABLE IF EXISTS randallbrenes_dnd_monsters CASCADE")

    """Upgrade schema."""
    op.create_table(
        'randallbrenes_dnd_monsters',
        sa.Column('index', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('desc', sa.String(), nullable=True),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('subtype', sa.String(), nullable=True),
        sa.Column('alignment', sa.String(), nullable=True),
        sa.Column('armor_class', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('hit_points', sa.Integer(), nullable=True),
        sa.Column('hit_dice', sa.String(), nullable=True),
        sa.Column('hit_points_roll', sa.String(), nullable=True),
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
        sa.Column('languages', sa.String(), nullable=True),
        sa.Column('challenge_rating', sa.Float(), nullable=True), 
        sa.Column('proficiency_bonus', sa.Integer(), nullable=True),
        sa.Column('xp', sa.Integer(), nullable=True),
        sa.Column('special_abilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('legendary_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('forms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reactions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('index')
    )


def downgrade() -> None:
    """Downgrade schema."""
    """Drop table to revert migration"""
    op.drop_table('randallbrenes_dnd_monsters')
 