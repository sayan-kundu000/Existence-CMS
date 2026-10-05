"""add skill domain column

Revision ID: 020_add_skill_domain
Revises: 019_education_level_diploma
Create Date: 2026-10-01 21:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '020_add_skill_domain'
down_revision: Union[str, None] = '019_education_level_diploma'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('skills')]
    indexes = [idx['name'] for idx in inspector.get_indexes('skills')]
    with op.batch_alter_table('skills') as batch_op:
        if 'domain' not in columns:
            batch_op.add_column(sa.Column('domain', sa.String(length=100), nullable=True))
        if 'ix_skills_domain' not in indexes:
            batch_op.create_index('ix_skills_domain', ['domain'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('skills')]
    indexes = [idx['name'] for idx in inspector.get_indexes('skills')]
    with op.batch_alter_table('skills') as batch_op:
        if 'ix_skills_domain' in indexes:
            batch_op.drop_index('ix_skills_domain')
        if 'domain' in columns:
            batch_op.drop_column('domain')

