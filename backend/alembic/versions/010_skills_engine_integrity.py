"""skills_engine_integrity

Revision ID: 010_skills_engine_integrity
Revises: 009_profile_email_visibility_and_indexes
Create Date: 2026-09-30 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010_skills_engine_integrity'
down_revision: Union[str, None] = '009_profile_email_visibility_and_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Performance query indexes
    op.create_index('ix_skills_category', 'skills', ['category'], unique=False)
    op.create_index('ix_skills_rating', 'skills', ['rating'], unique=False)
    op.create_index('ix_skills_visibility', 'skills', ['is_visible'], unique=False)

    # 2. Case-insensitive unique skill name per profile index
    op.execute("CREATE UNIQUE INDEX ix_skills_profile_lower_name ON skills (profile_id, lower(name))")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_skills_profile_lower_name")
    op.drop_index('ix_skills_visibility', table_name='skills')
    op.drop_index('ix_skills_rating', table_name='skills')
    op.drop_index('ix_skills_category', table_name='skills')
