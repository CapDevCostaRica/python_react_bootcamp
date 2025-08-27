"""empty message

Revision ID: 4c948fe4187e
Revises: 420c3f86afb0, 9786a2e1878e
Create Date: 2025-08-27 12:58:18.999930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c948fe4187e'
down_revision: Union[str, Sequence[str], None] = ('420c3f86afb0', '9786a2e1878e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
