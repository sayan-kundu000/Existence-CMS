"""profile_emails_and_data

Revision ID: 002_profile_emails_and_data
Revises: e65b956aa4c4
Create Date: 2026-09-28 18:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_profile_emails_and_data'
down_revision: Union[str, None] = 'e65b956aa4c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create profile_emails table
    op.create_table(
        'profile_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('label', sa.String(length=50), server_default='Primary', nullable=False),
        sa.Column('is_primary', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('display_order >= 0', name='check_profile_email_display_order')
    )
    op.create_index(op.f('ix_profile_emails_id'), 'profile_emails', ['id'], unique=False)
    op.create_index(op.f('ix_profile_emails_profile_id'), 'profile_emails', ['profile_id'], unique=False)
    op.create_index(op.f('ix_profile_emails_email'), 'profile_emails', ['email'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_profile_emails_email'), table_name='profile_emails')
    op.drop_index(op.f('ix_profile_emails_profile_id'), table_name='profile_emails')
    op.drop_index(op.f('ix_profile_emails_id'), table_name='profile_emails')
    op.drop_table('profile_emails')
