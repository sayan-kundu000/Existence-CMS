"""profile_email_visibility_and_indexes

Revision ID: 009_profile_email_visibility_and_indexes
Revises: 008_postgresql_indexes_and_integrity
Create Date: 2026-09-29 16:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_profile_email_visibility_and_indexes'
down_revision: Union[str, None] = '008_postgresql_indexes_and_integrity'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add is_public column to profile_emails
    with op.batch_alter_table('profile_emails', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_public', sa.Boolean(), server_default='1', nullable=False))
        batch_op.create_index('ix_profile_emails_is_primary', ['profile_id', 'is_primary'], unique=False)
        batch_op.create_index('ix_profile_emails_is_public', ['profile_id', 'is_public'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('profile_emails', schema=None) as batch_op:
        batch_op.drop_index('ix_profile_emails_is_public')
        batch_op.drop_index('ix_profile_emails_is_primary')
        batch_op.drop_column('is_public')
