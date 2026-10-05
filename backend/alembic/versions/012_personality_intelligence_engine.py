"""personality_intelligence_engine

Revision ID: 012_personality_intelligence_engine
Revises: 011_skill_categories_expansion
Create Date: 2026-09-30 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '012_personality_intelligence_engine'
down_revision: Union[str, None] = '011_skill_categories_expansion'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_public to assessment_results
    with op.batch_alter_table("assessment_results") as batch_op:
        batch_op.add_column(
            sa.Column("is_public", sa.Boolean(), server_default=sa.text("1"), nullable=False)
        )
        batch_op.create_index("ix_assessment_results_is_public", ["is_public"], unique=False)
        batch_op.create_index("ix_assessment_results_type_completed", ["assessment_type", "completed_at"], unique=False)

    # 2. Add status to assessment_definitions
    with op.batch_alter_table("assessment_definitions") as batch_op:
        batch_op.add_column(
            sa.Column("status", sa.String(length=20), server_default="PUBLISHED", nullable=False)
        )

    # 3. Add progress_index to assessment_sessions
    with op.batch_alter_table("assessment_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("progress_index", sa.Integer(), server_default="0", nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("assessment_sessions") as batch_op:
        batch_op.drop_column("progress_index")

    with op.batch_alter_table("assessment_definitions") as batch_op:
        batch_op.drop_column("status")

    with op.batch_alter_table("assessment_results") as batch_op:
        batch_op.drop_index("ix_assessment_results_type_completed")
        batch_op.drop_index("ix_assessment_results_is_public")
        batch_op.drop_column("is_public")
