"""skills_hobbies_interests_domain

Revision ID: 004_skills_hobbies_interests_domain
Revises: 003_education_and_experience_domain
Create Date: 2026-09-28 18:54:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_skills_hobbies_interests_domain'
down_revision: Union[str, None] = '003_education_and_experience_domain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update skills table
    with op.batch_alter_table('skills') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_visible', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.create_foreign_key('fk_skills_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_skills_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_skill_rating',
            'rating >= 1 AND rating <= 7'
        )
        batch_op.create_check_constraint(
            'check_skill_display_order',
            'display_order >= 0'
        )
        batch_op.create_check_constraint(
            'check_skill_name_not_empty',
            'length(trim(name)) > 0'
        )

    # 2. Update hobbies table
    with op.batch_alter_table('hobbies') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_visible', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.create_foreign_key('fk_hobbies_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_hobbies_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_hobby_display_order',
            'display_order >= 0'
        )
        batch_op.create_check_constraint(
            'check_hobby_name_not_empty',
            'length(trim(name)) > 0'
        )

    # 3. Update interests table
    with op.batch_alter_table('interests') as batch_op:
        batch_op.add_column(sa.Column('profile_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_visible', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), server_default='0', nullable=False))
        batch_op.create_foreign_key('fk_interests_profile_id', 'profiles', ['profile_id'], ['id'], ondelete='CASCADE')
        batch_op.create_index(op.f('ix_interests_profile_id'), ['profile_id'], unique=False)
        batch_op.create_check_constraint(
            'check_interest_display_order',
            'display_order >= 0'
        )
        batch_op.create_check_constraint(
            'check_interest_name_not_empty',
            'length(trim(name)) > 0'
        )


def downgrade() -> None:
    with op.batch_alter_table('interests') as batch_op:
        batch_op.drop_constraint('check_interest_name_not_empty', type_='check')
        batch_op.drop_constraint('check_interest_display_order', type_='check')
        batch_op.drop_index(op.f('ix_interests_profile_id'))
        batch_op.drop_constraint('fk_interests_profile_id', type_='foreignkey')
        batch_op.drop_column('display_order')
        batch_op.drop_column('is_visible')
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('hobbies') as batch_op:
        batch_op.drop_constraint('check_hobby_name_not_empty', type_='check')
        batch_op.drop_constraint('check_hobby_display_order', type_='check')
        batch_op.drop_index(op.f('ix_hobbies_profile_id'))
        batch_op.drop_constraint('fk_hobbies_profile_id', type_='foreignkey')
        batch_op.drop_column('display_order')
        batch_op.drop_column('is_visible')
        batch_op.drop_column('profile_id')

    with op.batch_alter_table('skills') as batch_op:
        batch_op.drop_constraint('check_skill_name_not_empty', type_='check')
        batch_op.drop_constraint('check_skill_display_order', type_='check')
        batch_op.drop_constraint('check_skill_rating', type_='check')
        batch_op.drop_index(op.f('ix_skills_profile_id'))
        batch_op.drop_constraint('fk_skills_profile_id', type_='foreignkey')
        batch_op.drop_column('display_order')
        batch_op.drop_column('is_visible')
        batch_op.drop_column('profile_id')
