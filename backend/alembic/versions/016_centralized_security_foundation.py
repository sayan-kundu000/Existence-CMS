"""centralized_security_foundation

Revision ID: 016_centralized_security_foundation
Revises: 015_projects_engine_schema
Create Date: 2026-10-01 15:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '016_centralized_security_foundation'
down_revision: Union[str, None] = '015_projects_engine_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add user_id to profiles table with foreign key to admin_users
    with op.batch_alter_table('profiles') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_profiles_user_id_admin_users',
            'admin_users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )
        batch_op.create_index(op.f('ix_profiles_user_id'), ['user_id'], unique=False)

    # 2. Link existing profiles to default admin account if available
    try:
        op.execute(
            "UPDATE profiles SET user_id = (SELECT id FROM admin_users ORDER BY id ASC LIMIT 1) "
            "WHERE user_id IS NULL AND (SELECT COUNT(*) FROM admin_users) > 0"
        )
    except Exception:
        pass


def downgrade() -> None:
    with op.batch_alter_table('profiles') as batch_op:
        batch_op.drop_index(op.f('ix_profiles_user_id'))
        batch_op.drop_constraint('fk_profiles_user_id_admin_users', type_='foreignkey')
        batch_op.drop_column('user_id')
