"""align_legacy_column_defaults

Revision ID: 017_align_legacy_column_defaults
Revises: 016_centralized_security_foundation
Create Date: 2026-10-01 16:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '017_align_legacy_column_defaults'
down_revision: Union[str, None] = '016_centralized_security_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update educations: make legacy ordering column nullable with default 0
    with op.batch_alter_table('educations') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=True, server_default='0')

    # 2. Update work_experiences: make legacy ordering column nullable with default 0
    with op.batch_alter_table('work_experiences') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=True, server_default='0')

    # 3. Update hobbies: make legacy ordering & visibility columns nullable with defaults
    with op.batch_alter_table('hobbies') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=True, server_default='0')
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=True, server_default='1')

    # 4. Update interests: make legacy ordering & visibility columns nullable with defaults
    with op.batch_alter_table('interests') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=True, server_default='0')
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=True, server_default='1')

    # 5. Update skills: make legacy ordering, visibility & metadata_info columns nullable with defaults
    with op.batch_alter_table('skills') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=True, server_default='0')
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=True, server_default='1')
        batch_op.alter_column('metadata_info', existing_type=sa.Text(), nullable=True, server_default='{}')

    # 6. Update audit_events: make legacy event_type & timestamp columns nullable with defaults
    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.alter_column('event_type', existing_type=sa.String(length=50), nullable=True, server_default='')
        batch_op.alter_column('timestamp', existing_type=sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP'))

    # 7. Update content_revisions: make legacy entity_name, editor_username, current_snapshot nullable with defaults
    with op.batch_alter_table('content_revisions') as batch_op:
        batch_op.alter_column('entity_name', existing_type=sa.String(length=50), nullable=True, server_default='')
        batch_op.alter_column('editor_username', existing_type=sa.String(length=50), nullable=True, server_default='admin')
        batch_op.alter_column('current_snapshot', existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('content_revisions') as batch_op:
        batch_op.alter_column('current_snapshot', existing_type=sa.Text(), nullable=True)
        batch_op.alter_column('editor_username', existing_type=sa.String(length=50), nullable=False, server_default='admin')
        batch_op.alter_column('entity_name', existing_type=sa.String(length=50), nullable=False, server_default='')

    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.alter_column('event_type', existing_type=sa.String(length=50), nullable=False, server_default='')

    with op.batch_alter_table('skills') as batch_op:
        batch_op.alter_column('metadata_info', existing_type=sa.Text(), nullable=False, server_default='{}')
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=False, server_default='1')
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=False, server_default='0')

    with op.batch_alter_table('interests') as batch_op:
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=False, server_default='1')
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=False, server_default='0')

    with op.batch_alter_table('hobbies') as batch_op:
        batch_op.alter_column('visibility', existing_type=sa.Boolean(), nullable=False, server_default='1')
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=False, server_default='0')

    with op.batch_alter_table('work_experiences') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=False, server_default='0')

    with op.batch_alter_table('educations') as batch_op:
        batch_op.alter_column('ordering', existing_type=sa.Integer(), nullable=False, server_default='0')
