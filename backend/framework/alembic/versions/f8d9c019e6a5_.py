"""empty message

Revision ID: f8d9c019e6a5
Revises: 9447e6c57ccb
Create Date: 2025-08-27 19:06:21.515142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8d9c019e6a5'
down_revision: Union[str, Sequence[str], None] = '9447e6c57ccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
