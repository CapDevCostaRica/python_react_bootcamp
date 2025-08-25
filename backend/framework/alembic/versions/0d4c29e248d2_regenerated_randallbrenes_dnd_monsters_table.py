"""Update randallbrenes_dnd_monsters table

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
table_name = 'randallbrenes_dnd_monsters'

def upgrade() -> None:
    """Add new columns and update types preserving existing data."""
    conn = op.get_bind()

    columns_to_add = {
        'desc': sa.String(),
        'subtype': sa.String(),
        'proficiencies': postgresql.JSONB(),
        'damage_vulnerabilities': postgresql.JSONB(),
        'damage_resistances': postgresql.JSONB(),
        'damage_immunities': postgresql.JSONB(),
        'condition_immunities': postgresql.JSONB(),
        'senses': postgresql.JSONB(),
        'challenge_rating': sa.Float(),
        'special_abilities': postgresql.JSONB(),
        'actions': postgresql.JSONB(),
        'legendary_actions': postgresql.JSONB(),
        'forms': postgresql.JSONB(),
        'reactions': postgresql.JSONB()
    }

    # Add columns if they don't exist
    existing_columns = [c[0] for c in conn.execute(
        sa.text("SELECT column_name FROM information_schema.columns WHERE table_name=:table"),
        {"table": table_name}
    )]
    
    for col_name, col_type in columns_to_add.items():
        if col_name not in existing_columns:
            op.add_column(table_name, sa.Column(col_name, col_type, nullable=True))

    # Convert string columns to integer
    int_columns = ['dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    for col in int_columns:
        if col in existing_columns:
            op.alter_column(
                table_name,
                col,
                existing_type=sa.String(),
                type_=sa.Integer(),
                postgresql_using=f"{col}::integer"
            )

def downgrade() -> None:
    """Remove newly added columns and revert type changes."""
    # Drop newly added columns
    columns_to_drop = [
        'desc', 'subtype', 'proficiencies', 'damage_vulnerabilities',
        'damage_resistances', 'damage_immunities', 'condition_immunities',
        'senses', 'challenge_rating', 'special_abilities', 'actions',
        'legendary_actions', 'forms', 'reactions'
    ]
    for col in columns_to_drop:
        op.drop_column(table_name, col)

    # Revert integer columns back to string
    int_columns = ['dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    for col in int_columns:
        op.alter_column(
            table_name,
            col,
            existing_type=sa.Integer(),
            type_=sa.String(),
            postgresql_using=f"{col}::text"
        )
