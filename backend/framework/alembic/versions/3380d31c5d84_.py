"""empty message

Revision ID: 3380d31c5d84
Revises: 6b57418ff7de, bac07e2df5a7
Create Date: 2025-08-27 16:28:37.389438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3380d31c5d84'
down_revision: Union[str, Sequence[str], None] = ('6b57418ff7de', 'bac07e2df5a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
