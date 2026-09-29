"""authentication_and_pin_security

Revision ID: 005_authentication_and_pin_security
Revises: 004_skills_hobbies_interests_domain
Create Date: 2026-09-28 18:56:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_authentication_and_pin_security'
down_revision: Union[str, None] = '004_skills_hobbies_interests_domain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename users to admin_users
    op.rename_table('users', 'admin_users')

    # 2. Update admin_users table
    with op.batch_alter_table('admin_users') as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), server_default='', nullable=False))
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))

    # Copy data from hashed_password to password_hash
    op.execute("UPDATE admin_users SET password_hash = hashed_password WHERE password_hash = ''")

    # 3. Create auth_sessions table
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('token_identifier', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_sessions_id'), 'auth_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_auth_sessions_admin_user_id'), 'auth_sessions', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_auth_sessions_token_identifier'), 'auth_sessions', ['token_identifier'], unique=True)

    # 4. Update pin_security table
    with op.batch_alter_table('pin_security') as batch_op:
        batch_op.add_column(sa.Column('admin_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('pin_hash', sa.String(length=255), server_default='', nullable=False))

    op.execute("UPDATE pin_security SET admin_user_id = user_id WHERE admin_user_id IS NULL")
    op.execute("UPDATE pin_security SET pin_hash = hashed_pin WHERE pin_hash = ''")

    with op.batch_alter_table('pin_security') as batch_op:
        batch_op.create_foreign_key('fk_pin_security_admin_user_id', 'admin_users', ['admin_user_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_pin_security_admin_user_id'), ['admin_user_id'], unique=False)

    # 5. Create pin_verification_sessions table
    op.create_table(
        'pin_verification_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('verification_identifier', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pin_verification_sessions_id'), 'pin_verification_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_pin_verification_sessions_admin_user_id'), 'pin_verification_sessions', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_pin_verification_sessions_verification_identifier'), 'pin_verification_sessions', ['verification_identifier'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_pin_verification_sessions_verification_identifier'), table_name='pin_verification_sessions')
    op.drop_index(op.f('ix_pin_verification_sessions_admin_user_id'), table_name='pin_verification_sessions')
    op.drop_index(op.f('ix_pin_verification_sessions_id'), table_name='pin_verification_sessions')
    op.drop_table('pin_verification_sessions')

    with op.batch_alter_table('pin_security') as batch_op:
        batch_op.drop_index(op.f('ix_pin_security_admin_user_id'))
        batch_op.drop_constraint('fk_pin_security_admin_user_id', type_='foreignkey')
        batch_op.drop_column('pin_hash')
        batch_op.drop_column('admin_user_id')

    op.drop_index(op.f('ix_auth_sessions_token_identifier'), table_name='auth_sessions')
    op.drop_index(op.f('ix_auth_sessions_admin_user_id'), table_name='auth_sessions')
    op.drop_index(op.f('ix_auth_sessions_id'), table_name='auth_sessions')
    op.drop_table('auth_sessions')

    with op.batch_alter_table('admin_users') as batch_op:
        batch_op.drop_column('last_login_at')
        batch_op.drop_column('password_hash')

    op.rename_table('admin_users', 'users')
