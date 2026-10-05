"""assessment_definition_version_unique

Revision ID: 014_assessment_definition_version_unique
Revises: 013_assessment_session_version
Create Date: 2026-09-30 10:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '014_assessment_definition_version_unique'
down_revision: Union[str, None] = '013_assessment_session_version'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("assessment_definitions") as batch_op:
        try:
            batch_op.drop_index("ix_assessment_definitions_code")
        except Exception:
            pass
        batch_op.create_index("ix_assessment_definitions_code", ["code"], unique=False)
        batch_op.create_unique_constraint(
            "uq_assessment_definition_code_version",
            ["code", "version"]
        )


def downgrade() -> None:
    with op.batch_alter_table("assessment_definitions") as batch_op:
        batch_op.drop_constraint("uq_assessment_definition_code_version", type_="unique")
        batch_op.drop_index("ix_assessment_definitions_code")
        batch_op.create_index("ix_assessment_definitions_code", ["code"], unique=True)
