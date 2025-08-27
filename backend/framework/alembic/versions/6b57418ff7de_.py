"""empty message

Revision ID: 6b57418ff7de
Revises: 0d4c29e248d1, 4c948fe4187e
Create Date: 2025-08-27 16:22:15.986739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b57418ff7de'
down_revision: Union[str, Sequence[str], None] = ('0d4c29e248d1', '4c948fe4187e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
