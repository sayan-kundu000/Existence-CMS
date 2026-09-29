"""education_and_experience_domain

Revision ID: 003_education_and_experience_domain
Revises: 002_profile_emails_and_data
Create Date: 2026-09-28 18:52:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_education_and_experience_domain'
down_revision: Union[str, None] = '002_profile_emails_and_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update educations table
    with op.batch_alter_table('educations') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('start_month', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('start_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('end_month', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('end_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.create_foreign_key('fk_educations_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_educations_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_education_level',
            "level IN ('Doctorate', 'Post Graduate', 'Graduate', 'Undergraduate', 'High School', 'Matriculation')"
        )
        batch_op.create_check_constraint(
            'check_education_start_month',
            "start_month IS NULL OR (start_month >= 1 AND start_month <= 12)"
        )
        batch_op.create_check_constraint(
            'check_education_end_month',
            "end_month IS NULL OR (end_month >= 1 AND end_month <= 12)"
        )
        batch_op.create_check_constraint(
            'check_education_start_year',
            "start_year IS NULL OR start_year > 0"
        )
        batch_op.create_check_constraint(
            'check_education_end_year',
            "end_year IS NULL OR end_year > 0"
        )
        batch_op.create_check_constraint(
            'check_education_studying_no_end',
            "currently_studying = 0 OR currently_studying = FALSE OR (end_month IS NULL AND end_year IS NULL)"
        )
        batch_op.create_check_constraint(
            'check_education_dates',
            "currently_studying = 1 OR currently_studying = TRUE OR start_year IS NULL OR end_year IS NULL OR ("
            "end_year > start_year OR (end_year = start_year AND (end_month IS NULL OR start_month IS NULL OR end_month >= start_month))"
            ")"
        )
        batch_op.create_check_constraint(
            'check_education_display_order',
            "display_order >= 0"
        )

    # 2. Rename experiences table to work_experiences
    op.rename_table('experiences', 'work_experiences')

    # 3. Update work_experiences table
    with op.batch_alter_table('work_experiences') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('start_month', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('start_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('end_month', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('end_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.create_foreign_key('fk_work_experiences_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_work_experiences_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_work_mode',
            "work_mode IN ('On-site', 'Remote', 'Hybrid')"
        )
        batch_op.create_check_constraint(
            'check_experience_location',
            "(work_mode IN ('On-site', 'Hybrid') AND location IS NOT NULL AND length(trim(location)) > 0) OR (work_mode = 'Remote')"
        )
        batch_op.create_check_constraint(
            'check_experience_start_month',
            "start_month IS NULL OR (start_month >= 1 AND start_month <= 12)"
        )
        batch_op.create_check_constraint(
            'check_experience_end_month',
            "end_month IS NULL OR (end_month >= 1 AND end_month <= 12)"
        )
        batch_op.create_check_constraint(
            'check_experience_start_year',
            "start_year IS NULL OR start_year > 0"
        )
        batch_op.create_check_constraint(
            'check_experience_end_year',
            "end_year IS NULL OR end_year > 0"
        )
        batch_op.create_check_constraint(
            'check_experience_working_no_end',
            "currently_working = 0 OR currently_working = FALSE OR (end_month IS NULL AND end_year IS NULL)"
        )
        batch_op.create_check_constraint(
            'check_experience_dates',
            "currently_working = 1 OR currently_working = TRUE OR start_year IS NULL OR end_year IS NULL OR ("
            "end_year > start_year OR (end_year = start_year AND (end_month IS NULL OR start_month IS NULL OR end_month >= start_month))"
            ")"
        )
        batch_op.create_check_constraint(
            'check_experience_display_order',
            "display_order >= 0"
        )


def downgrade() -> None:
    with op.batch_alter_table('work_experiences') as batch_op:
        batch_op.drop_constraint('check_experience_display_order', type_='check')
        batch_op.drop_constraint('check_experience_dates', type_='check')
        batch_op.drop_constraint('check_experience_working_no_end', type_='check')
        batch_op.drop_constraint('check_experience_end_year', type_='check')
        batch_op.drop_constraint('check_experience_start_year', type_='check')
        batch_op.drop_constraint('check_experience_end_month', type_='check')
        batch_op.drop_constraint('check_experience_start_month', type_='check')
        batch_op.drop_constraint('check_experience_location', type_='check')
        batch_op.drop_constraint('check_work_mode', type_='check')
        batch_op.drop_index(op.f('ix_work_experiences_profile_id'))
        batch_op.drop_constraint('fk_work_experiences_profile_id', type_='foreignkey')
        batch_op.drop_column('display_order')
        batch_op.drop_column('end_year')
        batch_op.drop_column('end_month')
        batch_op.drop_column('start_year')
        batch_op.drop_column('start_month')
        batch_op.drop_column('profile_id')

    op.rename_table('work_experiences', 'experiences')

    with op.batch_alter_table('educations') as batch_op:
        batch_op.drop_constraint('check_education_display_order', type_='check')
        batch_op.drop_constraint('check_education_dates', type_='check')
        batch_op.drop_constraint('check_education_studying_no_end', type_='check')
        batch_op.drop_constraint('check_education_end_year', type_='check')
        batch_op.drop_constraint('check_education_start_year', type_='check')
        batch_op.drop_constraint('check_education_end_month', type_='check')
        batch_op.drop_constraint('check_education_start_month', type_='check')
        batch_op.drop_constraint('check_education_level', type_='check')
        batch_op.drop_index(op.f('ix_educations_profile_id'))
        batch_op.drop_constraint('fk_educations_profile_id', type_='foreignkey')
        batch_op.drop_column('display_order')
        batch_op.drop_column('end_year')
        batch_op.drop_column('end_month')
        batch_op.drop_column('start_year')
        batch_op.drop_column('start_month')
        batch_op.drop_column('profile_id')
