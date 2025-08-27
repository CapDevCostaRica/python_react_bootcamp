"""merge heads after rebase (odkeyo)

Revision ID: da82e22496b7
Revises: 36212e46cc4d, bac07e2df5a7
Create Date: 2025-08-27 23:36:58.808753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da82e22496b7'
down_revision: Union[str, Sequence[str], None] = ('36212e46cc4d', 'bac07e2df5a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
