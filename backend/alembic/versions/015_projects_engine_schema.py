"""projects_engine_schema

Revision ID: 015_projects_engine_schema
Revises: 014_assessment_definition_version_unique
Create Date: 2026-09-30 23:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '015_projects_engine_schema'
down_revision: Union[str, None] = '014_assessment_definition_version_unique'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Technologies Table
    op.create_table(
        'technologies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), server_default='Other', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_technologies_id', 'technologies', ['id'], unique=False)
    op.create_index('ix_technologies_name', 'technologies', ['name'], unique=True)
    op.create_index('ix_technologies_lower_name', 'technologies', [sa.text('lower(name)')], unique=True)

    # 2. Projects Table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('short_description', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='Completed', nullable=True),
        sa.Column('start_month', sa.Integer(), nullable=True),
        sa.Column('start_year', sa.Integer(), nullable=True),
        sa.Column('end_month', sa.Integer(), nullable=True),
        sa.Column('end_year', sa.Integer(), nullable=True),
        sa.Column('is_current', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_featured', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_visible', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_id', 'projects', ['id'], unique=False)
    op.create_index('ix_projects_profile_id', 'projects', ['profile_id'], unique=False)
    op.create_index('ix_projects_visibility', 'projects', ['is_visible'], unique=False)
    op.create_index('ix_projects_is_featured', 'projects', ['is_featured'], unique=False)
    op.create_index('ix_projects_status', 'projects', ['status'], unique=False)
    op.create_index('ix_projects_profile_lower_name', 'projects', ['profile_id', sa.text('lower(name)')], unique=True)

    # 3. Project Links Table (Multiple Links per Project)
    op.create_table(
        'project_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('link_type', sa.String(length=50), server_default='Live Demo', nullable=False),
        sa.Column('is_primary', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_visible', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_project_links_id', 'project_links', ['id'], unique=False)
    op.create_index('ix_project_links_project_id', 'project_links', ['project_id'], unique=False)
    op.create_index('ix_project_links_is_primary', 'project_links', ['project_id', 'is_primary'], unique=False)

    # 4. Project Technologies Association Table
    op.create_table(
        'project_technologies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('technology_id', sa.Integer(), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['technology_id'], ['technologies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'technology_id', name='uq_project_technology')
    )
    op.create_index('ix_project_technologies_id', 'project_technologies', ['id'], unique=False)
    op.create_index('ix_project_technologies_project_id', 'project_technologies', ['project_id'], unique=False)
    op.create_index('ix_project_technologies_technology_id', 'project_technologies', ['technology_id'], unique=False)

    # 5. Project Skills Association Table
    op.create_table(
        'project_skills',
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('project_id', 'skill_id')
    )


def downgrade() -> None:
    op.drop_table('project_skills')
    op.drop_table('project_technologies')
    op.drop_table('project_links')
    op.drop_table('projects')
    op.drop_table('technologies')
