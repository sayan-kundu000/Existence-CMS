"""education score and stream rules

Revision ID: 018_education_score_and_stream
Revises: 017_align_legacy_column_defaults
Create Date: 2026-10-01 17:42:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018_education_score_and_stream'
down_revision: Union[str, None] = '017_align_legacy_column_defaults'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('educations') as batch_op:
        batch_op.alter_column('stream', existing_type=sa.String(120), nullable=True)
        batch_op.add_column(sa.Column('score_type', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('score_value', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('educations') as batch_op:
        batch_op.drop_column('score_value')
        batch_op.drop_column('score_type')
        batch_op.alter_column('stream', existing_type=sa.String(120), nullable=False)
