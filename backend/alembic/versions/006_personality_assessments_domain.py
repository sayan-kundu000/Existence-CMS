"""personality_assessments_domain

Revision ID: 006_personality_assessments_domain
Revises: 005_authentication_and_pin_security
Create Date: 2026-09-28 18:58:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_personality_assessments_domain'
down_revision: Union[str, None] = '005_authentication_and_pin_security'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update assessment_definitions
    with op.batch_alter_table('assessment_definitions') as batch_op:
        batch_op.add_column(sa.Column('code', sa.String(length=30), server_default='', nullable=False))
        batch_op.add_column(sa.Column('version', sa.String(length=20), server_default='1.0', nullable=False))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))

    op.execute("UPDATE assessment_definitions SET code = assessment_type WHERE code = ''")
    op.execute("UPDATE assessment_definitions SET is_active = is_configured")

    with op.batch_alter_table('assessment_definitions') as batch_op:
        batch_op.create_index(op.f('ix_assessment_definitions_code'), ['code'], unique=True)

    # 2. Update assessment_questions
    with op.batch_alter_table('assessment_questions') as batch_op:
        batch_op.add_column(sa.Column('assessment_definition_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('question_key', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('question_text', sa.Text(), server_default='', nullable=False))
        batch_op.add_column(sa.Column('question_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('scoring_configuration', sa.Text(), server_default='{}', nullable=False))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.execute("UPDATE assessment_questions SET question_text = text WHERE question_text = ''")
    op.execute("UPDATE assessment_questions SET question_order = ordering")
    op.execute("UPDATE assessment_questions SET question_key = id WHERE question_key IS NULL")

    with op.batch_alter_table('assessment_questions') as batch_op:
        batch_op.create_foreign_key('fk_assessment_questions_def_id', 'assessment_definitions', ['assessment_definition_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_assessment_questions_assessment_definition_id'), ['assessment_definition_id'], unique=False)

    # 3. Update assessment_sessions
    with op.batch_alter_table('assessment_sessions') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('assessment_definition_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.create_foreign_key('fk_assessment_sessions_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='SET NULL')
        batch_op.create_foreign_key('fk_assessment_sessions_def_id', 'assessment_definitions', ['assessment_definition_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_assessment_sessions_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_assessment_session_status',
            "status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'ABANDONED')"
        )

    # 4. Update assessment_responses: add response_value, answered_at, and UniqueConstraint(session_id, question_id)
    with op.batch_alter_table('assessment_responses') as batch_op:
        batch_op.add_column(sa.Column('response_value', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.execute("UPDATE assessment_responses SET response_value = selected_value WHERE response_value = 0")
    op.execute("UPDATE assessment_responses SET answered_at = created_at")

    with op.batch_alter_table('assessment_responses') as batch_op:
        batch_op.create_index(op.f('ix_assessment_responses_question_id'), ['question_id'], unique=False)
        batch_op.create_unique_constraint('uq_assessment_response_session_question', ['session_id', 'question_id'])

    # 5. Update assessment_results
    with op.batch_alter_table('assessment_results') as batch_op:
        batch_op.add_column(sa.Column('assessment_definition_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('result_version', sa.String(length=20), server_default='1.0', nullable=False))
        batch_op.add_column(sa.Column('summary_data', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.create_foreign_key('fk_assessment_results_def_id', 'assessment_definitions', ['assessment_definition_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index(op.f('ix_assessment_results_assessment_definition_id'), ['assessment_definition_id'], unique=False)

    # 6. Update personality_trait_scores
    with op.batch_alter_table('personality_trait_scores') as batch_op:
        batch_op.add_column(sa.Column('trait_code', sa.String(length=80), server_default='', nullable=False))
        batch_op.add_column(sa.Column('score', sa.Float(), server_default='0.0', nullable=False))
        batch_op.add_column(sa.Column('normalized_score', sa.Float(), server_default='0.0', nullable=False))

    op.execute("UPDATE personality_trait_scores SET trait_code = trait_name WHERE trait_code = ''")
    op.execute("UPDATE personality_trait_scores SET score = score_value")
    op.execute("UPDATE personality_trait_scores SET normalized_score = percentage")

    with op.batch_alter_table('personality_trait_scores') as batch_op:
        batch_op.create_index(op.f('ix_personality_trait_scores_trait_code'), ['trait_code'], unique=False)

    # 7. Update soft_skill_records
    with op.batch_alter_table('soft_skill_records') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
        batch_op.create_foreign_key('fk_soft_skill_records_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_soft_skill_records_profile_id'), ['profile_id'], unique=False)

    # 8. Update strength_records
    with op.batch_alter_table('strength_records') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('title', sa.String(length=255), server_default='', nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.execute("UPDATE strength_records SET title = description WHERE title = ''")

    with op.batch_alter_table('strength_records') as batch_op:
        batch_op.create_foreign_key('fk_strength_records_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_strength_records_profile_id'), ['profile_id'], unique=False)

    # 9. Update weakness_records
    with op.batch_alter_table('weakness_records') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('title', sa.String(length=255), server_default='', nullable=False))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    op.execute("UPDATE weakness_records SET title = description WHERE title = ''")

    with op.batch_alter_table('weakness_records') as batch_op:
        batch_op.create_foreign_key('fk_weakness_records_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_weakness_records_profile_id'), ['profile_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('weakness_records') as batch_op:
        batch_op.drop_index(op.f('ix_weakness_records_profile_id'))
        batch_op.drop_constraint('fk_weakness_records_profile_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('title')

    with op.batch_alter_table('strength_records') as batch_op:
        batch_op.drop_index(op.f('ix_strength_records_profile_id'))
        batch_op.drop_constraint('fk_strength_records_profile_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('title')

    with op.batch_alter_table('soft_skill_records') as batch_op:
        batch_op.drop_index(op.f('ix_soft_skill_records_profile_id'))
        batch_op.drop_constraint('fk_soft_skill_records_profile_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('description')
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('personality_trait_scores') as batch_op:
        batch_op.drop_index(op.f('ix_personality_trait_scores_trait_code'))
        batch_op.drop_column('normalized_score')
        batch_op.drop_column('score')
        batch_op.drop_column('trait_code')

    with op.batch_alter_table('assessment_results') as batch_op:
        batch_op.drop_index(op.f('ix_assessment_results_assessment_definition_id'))
        batch_op.drop_constraint('fk_assessment_results_def_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('summary_data')
        batch_op.drop_column('result_version')
        batch_op.drop_column('assessment_definition_id')

    with op.batch_alter_table('assessment_responses') as batch_op:
        batch_op.drop_constraint('uq_assessment_response_session_question', type_='unique')
        batch_op.drop_index(op.f('ix_assessment_responses_question_id'))
        batch_op.drop_column('answered_at')
        batch_op.drop_column('response_value')

    with op.batch_alter_table('assessment_sessions') as batch_op:
        batch_op.drop_constraint('check_assessment_session_status', type_='check')
        batch_op.drop_index(op.f('ix_assessment_sessions_profile_id'))
        batch_op.drop_constraint('fk_assessment_sessions_def_id', type_='foreignkey')
        batch_op.drop_constraint('fk_assessment_sessions_profile_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('assessment_definition_id')
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('assessment_questions') as batch_op:
        batch_op.drop_index(op.f('ix_assessment_questions_assessment_definition_id'))
        batch_op.drop_constraint('fk_assessment_questions_def_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('is_active')
        batch_op.drop_column('scoring_configuration')
        batch_op.drop_column('question_order')
        batch_op.drop_column('question_text')
        batch_op.drop_column('question_key')
        batch_op.drop_column('assessment_definition_id')

    with op.batch_alter_table('assessment_definitions') as batch_op:
        batch_op.drop_index(op.f('ix_assessment_definitions_code'))
        batch_op.drop_column('is_active')
        batch_op.drop_column('version')
        batch_op.drop_column('code')
