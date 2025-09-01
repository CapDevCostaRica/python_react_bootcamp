"""empty message

Revision ID: 1bbdc41ad0e5
Revises: d53164abfe4b, randymorales_monster_cache
Create Date: 2025-08-28 14:36:19.287045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bbdc41ad0e5'
down_revision: Union[str, Sequence[str], None] = ('d53164abfe4b', 'randymorales_monster_cache')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
