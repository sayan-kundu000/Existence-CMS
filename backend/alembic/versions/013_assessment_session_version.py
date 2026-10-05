"""assessment_session_version

Revision ID: 013_assessment_session_version
Revises: 012_personality_intelligence_engine
Create Date: 2026-09-30 10:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '013_assessment_session_version'
down_revision: Union[str, None] = '012_personality_intelligence_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("assessment_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("assessment_version", sa.String(length=20), server_default="1.0", nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("assessment_sessions") as batch_op:
        batch_op.drop_column("assessment_version")
