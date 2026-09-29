"""postgresql_indexes_and_integrity

Revision ID: 008_postgresql_indexes_and_integrity
Revises: 007_content_revisions_and_audit_domain
Create Date: 2026-09-28 19:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_postgresql_indexes_and_integrity'
down_revision: Union[str, None] = '007_content_revisions_and_audit_domain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite & performance indexes
    op.create_index('ix_educations_profile_order', 'educations', ['profile_id', 'display_order'], unique=False)
    op.create_index('ix_work_exp_profile_order', 'work_experiences', ['profile_id', 'display_order'], unique=False)
    op.create_index('ix_skills_profile_order', 'skills', ['profile_id', 'display_order'], unique=False)
    op.create_index('ix_hobbies_profile_order', 'hobbies', ['profile_id', 'display_order'], unique=False)
    op.create_index('ix_interests_profile_order', 'interests', ['profile_id', 'display_order'], unique=False)
    op.create_index('ix_auth_sessions_user_token', 'auth_sessions', ['admin_user_id', 'token_identifier'], unique=False)
    op.create_index('ix_pin_verif_user_token', 'pin_verification_sessions', ['admin_user_id', 'verification_identifier'], unique=False)
    op.create_index('ix_assessment_sessions_prof_status', 'assessment_sessions', ['profile_id', 'status'], unique=False)
    op.create_index('ix_assessment_results_session_type', 'assessment_results', ['session_id', 'assessment_type'], unique=False)
    op.create_index('ix_content_revisions_type_id', 'content_revisions', ['entity_type', 'entity_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_content_revisions_type_id', table_name='content_revisions')
    op.drop_index('ix_assessment_results_session_type', table_name='assessment_results')
    op.drop_index('ix_assessment_sessions_prof_status', table_name='assessment_sessions')
    op.drop_index('ix_pin_verif_user_token', table_name='pin_verification_sessions')
    op.drop_index('ix_auth_sessions_user_token', table_name='auth_sessions')
    op.drop_index('ix_interests_profile_order', table_name='interests')
    op.drop_index('ix_hobbies_profile_order', table_name='hobbies')
    op.drop_index('ix_skills_profile_order', table_name='skills')
    op.drop_index('ix_work_exp_profile_order', table_name='work_experiences')
    op.drop_index('ix_educations_profile_order', table_name='educations')
