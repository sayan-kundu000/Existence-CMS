"""content_revisions_and_audit_domain

Revision ID: 007_content_revisions_and_audit_domain
Revises: 006_personality_assessments_domain
Create Date: 2026-09-28 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_content_revisions_and_audit_domain'
down_revision: Union[str, None] = '006_personality_assessments_domain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update content_revisions table
    with op.batch_alter_table('content_revisions') as batch_op:
        batch_op.add_column(sa.Column('entity_type', sa.String(length=50), server_default='', nullable=False))
        batch_op.add_column(sa.Column('revision_number', sa.Integer(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('changed_by', sa.String(length=50), server_default='admin', nullable=False))
        batch_op.add_column(sa.Column('snapshot', sa.Text(), nullable=True))

    op.execute("UPDATE content_revisions SET entity_type = entity_name WHERE entity_type = ''")
    op.execute("UPDATE content_revisions SET changed_by = editor_username")
    op.execute("UPDATE content_revisions SET snapshot = current_snapshot WHERE snapshot IS NULL")

    with op.batch_alter_table('content_revisions') as batch_op:
        batch_op.create_index(op.f('ix_content_revisions_entity_type'), ['entity_type'], unique=False)
        batch_op.create_check_constraint(
            'check_content_revision_action',
            "action IN ('CREATE', 'UPDATE', 'DELETE', 'RESTORE', 'PATCH')"
        )

    # 2. Update audit_events table
    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.add_column(sa.Column('actor_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('action', sa.String(length=50), server_default='', nullable=False))
        batch_op.add_column(sa.Column('entity_type', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('entity_id', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('request_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('metadata_json', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.execute("UPDATE audit_events SET actor_id = user_id WHERE actor_id IS NULL")
    op.execute("UPDATE audit_events SET action = event_type WHERE action = ''")
    op.execute("UPDATE audit_events SET metadata_json = details WHERE metadata_json IS NULL")
    op.execute("UPDATE audit_events SET created_at = timestamp")

    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.create_index(op.f('ix_audit_events_actor_id'), ['actor_id'], unique=False)
        batch_op.create_index(op.f('ix_audit_events_action'), ['action'], unique=False)
        batch_op.create_index(op.f('ix_audit_events_entity_type'), ['entity_type'], unique=False)
        batch_op.create_index(op.f('ix_audit_events_entity_id'), ['entity_id'], unique=False)
        batch_op.create_index(op.f('ix_audit_events_request_id'), ['request_id'], unique=False)
        batch_op.create_index(op.f('ix_audit_events_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('audit_events') as batch_op:
        batch_op.drop_index(op.f('ix_audit_events_created_at'))
        batch_op.drop_index(op.f('ix_audit_events_request_id'))
        batch_op.drop_index(op.f('ix_audit_events_entity_id'))
        batch_op.drop_index(op.f('ix_audit_events_entity_type'))
        batch_op.drop_index(op.f('ix_audit_events_action'))
        batch_op.drop_index(op.f('ix_audit_events_actor_id'))
        batch_op.drop_column('created_at')
        batch_op.drop_column('metadata_json')
        batch_op.drop_column('request_id')
        batch_op.drop_column('entity_id')
        batch_op.drop_column('entity_type')
        batch_op.drop_column('action')
        batch_op.drop_column('actor_id')

    with op.batch_alter_table('content_revisions') as batch_op:
        batch_op.drop_constraint('check_content_revision_action', type_='check')
        batch_op.drop_index(op.f('ix_content_revisions_entity_type'))
        batch_op.drop_column('snapshot')
        batch_op.drop_column('changed_by')
        batch_op.drop_column('revision_number')
        batch_op.drop_column('entity_type')
