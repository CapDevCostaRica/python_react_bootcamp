"""baseline ex2

Revision ID: 0d67121f2b83
Revises:
Create Date: 2025-09-02 04:51:08.529234
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0d67121f2b83"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ex2 schema (only the needed tables)."""

    # people
    op.create_table(
        "people",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(), nullable=False),
    )

    # physical (one-to-one con people por app; si quieres forzar 1-1, agrega Unique en person_id)
    op.create_table(
        "physical",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("nationality", sa.String(), nullable=True),
        sa.Column("hair_color", sa.String(), nullable=True),
        sa.Column("eye_color", sa.String(), nullable=True),
    )
    op.create_index("ix_physical_person_id", "physical", ["person_id"])

    # studies (unique por persona+degree+institution)
    op.create_table(
        "studies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("degree", sa.String(), nullable=True),
        sa.Column("institution", sa.String(), nullable=True),
        sa.UniqueConstraint("person_id", "degree", "institution", name="uq_study"),
    )
    op.create_index("ix_studies_person_id", "studies", ["person_id"])

    # families (unique por persona+relation+name)
    op.create_table(
        "families",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("relation", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.UniqueConstraint("person_id", "relation", "name", name="uq_family"),
    )
    op.create_index("ix_families_person_id", "families", ["person_id"])

    # favorite_foods (unique por persona+food)
    op.create_table(
        "favorite_foods",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("food", sa.String(), nullable=True),
        sa.UniqueConstraint("person_id", "food", name="uq_favorite_food"),
    )
    op.create_index("ix_favorite_foods_person_id", "favorite_foods", ["person_id"])
    op.create_index("ix_favorite_foods_food", "favorite_foods", ["food"])

    # hobbies (unique por persona+hobby)
    op.create_table(
        "hobbies",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("people.id"), nullable=True),
        sa.Column("hobby", sa.String(), nullable=True),
        sa.UniqueConstraint("person_id", "hobby", name="uq_hobby"),
    )
    op.create_index("ix_hobbies_person_id", "hobbies", ["person_id"])
    op.create_index("ix_hobbies_hobby", "hobbies", ["hobby"])


def downgrade() -> None:
    """Drop ex2 schema (reverse order of FKs)."""
    op.drop_index("ix_hobbies_hobby", table_name="hobbies")
    op.drop_index("ix_hobbies_person_id", table_name="hobbies")
    op.drop_table("hobbies")

    op.drop_index("ix_favorite_foods_food", table_name="favorite_foods")
    op.drop_index("ix_favorite_foods_person_id", table_name="favorite_foods")
    op.drop_table("favorite_foods")

    op.drop_index("ix_families_person_id", table_name="families")
    op.drop_table("families")

    op.drop_index("ix_studies_person_id", table_name="studies")
    op.drop_table("studies")

    op.drop_index("ix_physical_person_id", table_name="physical")
    op.drop_table("physical")

    op.drop_table("people")
