"""empty message

Revision ID: 9786a2e1878e
Revises: 5838f470f73b, cd4474e7e340
Create Date: 2025-08-27 08:24:23.366152

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9786a2e1878e'
down_revision: Union[str, Sequence[str], None] = ('5838f470f73b', 'cd4474e7e340')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass