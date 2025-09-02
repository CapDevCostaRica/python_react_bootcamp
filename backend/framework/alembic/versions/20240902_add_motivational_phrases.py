"""Add motivational_phrases table"""

from alembic import op
import sqlalchemy as sa


revision = "20240902_add_motivational_phrases"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "motivational_phrases",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phrase", sa.String(length=255), nullable=False, unique=True),
    )

def downgrade():
    op.drop_table("motivational_phrases")
