"""education level diploma update

Revision ID: 019_education_level_diploma
Revises: 018_education_score_and_stream
Create Date: 2026-10-01 18:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '019_education_level_diploma'
down_revision: Union[str, None] = '018_education_score_and_stream'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('educations') as batch_op:
        batch_op.drop_constraint('check_education_level', type_='check')
        batch_op.create_check_constraint(
            'check_education_level',
            "level IN ('Doctorate', 'Post Graduate', 'Graduate', 'Diploma', 'Undergraduate', 'High School', 'Matriculation')"
        )
    op.execute("UPDATE educations SET level = 'Diploma' WHERE level = 'Undergraduate'")


def downgrade() -> None:
    op.execute("UPDATE educations SET level = 'Undergraduate' WHERE level = 'Diploma'")
    with op.batch_alter_table('educations') as batch_op:
        batch_op.drop_constraint('check_education_level', type_='check')
        batch_op.create_check_constraint(
            'check_education_level',
            "level IN ('Doctorate', 'Post Graduate', 'Graduate', 'Undergraduate', 'High School', 'Matriculation')"
        )
