"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-03

This migration creates all initial database tables:
- users: User accounts and profiles
- interview_sessions: Interview practice sessions
- interview_questions: Questions within sessions
- interview_feedback: AI-generated feedback for sessions
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""
    
    # ============================================
    # Users Table
    # ============================================
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('target_role', sa.String(100), nullable=True),
        sa.Column('experience_level', sa.String(20), default='mid', nullable=True),
        sa.Column('skills', sa.JSON(), default=list, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # ============================================
    # Interview Sessions Table
    # ============================================
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('target_role', sa.String(100), nullable=True),
        sa.Column('target_company', sa.String(100), nullable=True),
        sa.Column('difficulty', sa.String(20), default='medium', nullable=True),
        sa.Column('status', sa.String(20), default='created', nullable=False),
        sa.Column('total_questions', sa.Integer(), default=0, nullable=True),
        sa.Column('answered_questions', sa.Integer(), default=0, nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('session_metadata', sa.JSON(), default=dict, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create index for user sessions lookup
    op.create_index('ix_sessions_user_created', 'interview_sessions', ['user_id', 'created_at'])
    
    # ============================================
    # Interview Questions Table
    # ============================================
    op.create_table(
        'interview_questions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('order_index', sa.Integer(), default=0, nullable=True),
        sa.Column('time_limit', sa.Integer(), default=120, nullable=True),
        sa.Column('expected_topics', sa.JSON(), default=list, nullable=True),
        sa.Column('audio_file_path', sa.String(500), nullable=True),
        sa.Column('audio_duration', sa.Integer(), nullable=True),
        sa.Column('transcription', sa.Text(), nullable=True),
        sa.Column('transcription_confidence', sa.Float(), nullable=True),
        sa.Column('evaluation_scores', sa.JSON(), default=dict, nullable=True),
        sa.Column('evaluation_feedback', sa.Text(), nullable=True),
        sa.Column('is_answered', sa.Boolean(), default=False, nullable=False),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create index for session questions lookup
    op.create_index('ix_questions_session_order', 'interview_questions', ['session_id', 'order_index'])
    
    # ============================================
    # Interview Feedback Table
    # ============================================
    op.create_table(
        'interview_feedback',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('interview_sessions.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('overall_rating', sa.String(50), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('strengths', sa.JSON(), default=list, nullable=True),
        sa.Column('weaknesses', sa.JSON(), default=list, nullable=True),
        sa.Column('suggestions', sa.JSON(), default=list, nullable=True),
        sa.Column('category_scores', sa.JSON(), default=dict, nullable=True),
        sa.Column('readiness_score', sa.Integer(), nullable=True),
        sa.Column('readiness_level', sa.String(50), nullable=True),
        sa.Column('next_steps', sa.JSON(), default=list, nullable=True),
        sa.Column('detailed_analysis', sa.JSON(), default=dict, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    
    # Drop feedback table first (depends on sessions)
    op.drop_table('interview_feedback')
    
    # Drop indexes
    op.drop_index('ix_questions_session_order', table_name='interview_questions')
    
    # Drop questions table (depends on sessions)
    op.drop_table('interview_questions')
    
    # Drop indexes
    op.drop_index('ix_sessions_user_created', table_name='interview_sessions')
    
    # Drop sessions table (depends on users)
    op.drop_table('interview_sessions')
    
    # Drop users table
    op.drop_table('users')
