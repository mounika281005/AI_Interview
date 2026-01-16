"""Add user statistics and session analytics

Revision ID: 002_add_analytics
Revises: 001_initial
Create Date: 2026-01-03

This migration adds analytics and statistics columns:
- User statistics for tracking progress
- Session analytics for detailed metrics
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_analytics'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add analytics columns."""
    
    # ============================================
    # Add User Statistics Columns
    # ============================================
    op.add_column('users', 
        sa.Column('total_sessions', sa.Integer(), default=0, nullable=True)
    )
    op.add_column('users', 
        sa.Column('total_questions_answered', sa.Integer(), default=0, nullable=True)
    )
    op.add_column('users', 
        sa.Column('total_practice_minutes', sa.Integer(), default=0, nullable=True)
    )
    op.add_column('users', 
        sa.Column('average_score', sa.Float(), nullable=True)
    )
    op.add_column('users', 
        sa.Column('highest_score', sa.Float(), nullable=True)
    )
    op.add_column('users', 
        sa.Column('current_streak', sa.Integer(), default=0, nullable=True)
    )
    op.add_column('users', 
        sa.Column('longest_streak', sa.Integer(), default=0, nullable=True)
    )
    op.add_column('users', 
        sa.Column('last_practice_date', sa.Date(), nullable=True)
    )
    
    # ============================================
    # Add Session Analytics Columns
    # ============================================
    op.add_column('interview_sessions',
        sa.Column('category_breakdown', sa.JSON(), default=dict, nullable=True)
    )
    op.add_column('interview_sessions',
        sa.Column('average_response_time', sa.Float(), nullable=True)
    )
    op.add_column('interview_sessions',
        sa.Column('audio_quality_score', sa.Float(), nullable=True)
    )
    
    # ============================================
    # Add Question Response Metrics
    # ============================================
    op.add_column('interview_questions',
        sa.Column('response_time_seconds', sa.Integer(), nullable=True)
    )
    op.add_column('interview_questions',
        sa.Column('word_count', sa.Integer(), nullable=True)
    )
    op.add_column('interview_questions',
        sa.Column('filler_word_count', sa.Integer(), nullable=True)
    )
    op.add_column('interview_questions',
        sa.Column('speaking_rate_wpm', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    """Remove analytics columns."""
    
    # Remove from interview_questions
    op.drop_column('interview_questions', 'speaking_rate_wpm')
    op.drop_column('interview_questions', 'filler_word_count')
    op.drop_column('interview_questions', 'word_count')
    op.drop_column('interview_questions', 'response_time_seconds')
    
    # Remove from interview_sessions
    op.drop_column('interview_sessions', 'audio_quality_score')
    op.drop_column('interview_sessions', 'average_response_time')
    op.drop_column('interview_sessions', 'category_breakdown')
    
    # Remove from users
    op.drop_column('users', 'last_practice_date')
    op.drop_column('users', 'longest_streak')
    op.drop_column('users', 'current_streak')
    op.drop_column('users', 'highest_score')
    op.drop_column('users', 'average_score')
    op.drop_column('users', 'total_practice_minutes')
    op.drop_column('users', 'total_questions_answered')
    op.drop_column('users', 'total_sessions')
