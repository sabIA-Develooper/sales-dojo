"""create initial tables

Revision ID: 001_initial
Revises:
Create Date: 2026-01-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='salesperson', nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('salesperson', 'manager', 'admin')", name='check_user_role'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_company_id', 'users', ['company_id'])
    op.create_index('idx_users_email', 'users', ['email'])

    # Create personas table
    op.create_table(
        'personas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='decision_maker'),
        sa.Column('personality_traits', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('pain_points', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('objections', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('background', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('decision_maker', 'influencer', 'gatekeeper', 'user')", name='check_persona_role'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_personas_company_id', 'personas', ['company_id'])

    # Create knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='document'),
        sa.Column('source_name', sa.String(length=500), nullable=False),
        # Vector column for pgvector - dimension 1536 for OpenAI text-embedding-3-small
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("source_type IN ('document', 'website', 'manual')", name='check_source_type'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_kb_company_id', 'knowledge_base', ['company_id'])

    # Create training_sessions table
    op.create_table(
        'training_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transcript', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='in_progress', nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=False), nullable=True),
        sa.CheckConstraint("status IN ('in_progress', 'completed', 'failed')", name='check_session_status'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_company_id', 'training_sessions', ['company_id'])
    op.create_index('idx_sessions_created_at', 'training_sessions', ['created_at'])
    op.create_index('idx_sessions_persona_id', 'training_sessions', ['persona_id'])
    op.create_index('idx_sessions_user_id', 'training_sessions', ['user_id'])

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('strengths', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('areas_for_improvement', postgresql.ARRAY(sa.Text()), server_default='{}', nullable=False),
        sa.Column('detailed_analysis', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('overall_score >= 0 AND overall_score <= 100', name='check_overall_score_range'),
        sa.ForeignKeyConstraint(['session_id'], ['training_sessions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('idx_feedback_session_id', 'feedback', ['session_id'])

    # Note: Vector index for knowledge_base.embedding should be created manually after data is populated
    # CREATE INDEX idx_kb_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


def downgrade() -> None:
    op.drop_index('idx_feedback_session_id', table_name='feedback')
    op.drop_table('feedback')

    op.drop_index('idx_sessions_user_id', table_name='training_sessions')
    op.drop_index('idx_sessions_persona_id', table_name='training_sessions')
    op.drop_index('idx_sessions_created_at', table_name='training_sessions')
    op.drop_index('idx_sessions_company_id', table_name='training_sessions')
    op.drop_table('training_sessions')

    op.drop_index('idx_kb_company_id', table_name='knowledge_base')
    op.drop_table('knowledge_base')

    op.drop_index('idx_personas_company_id', table_name='personas')
    op.drop_table('personas')

    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_company_id', table_name='users')
    op.drop_table('users')

    op.drop_table('companies')
