"""skill_categories_expansion

Revision ID: 011_skill_categories_expansion
Revises: 010_skills_engine_integrity
Create Date: 2026-09-30 09:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_skill_categories_expansion'
down_revision: Union[str, None] = '010_skills_engine_integrity'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("skills") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=sa.String(length=80),
            type_=sa.String(length=255),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("skills") as batch_op:
        batch_op.alter_column(
            "category",
            existing_type=sa.String(length=255),
            type_=sa.String(length=80),
            existing_nullable=False,
        )
