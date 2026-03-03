"""Add question bank and templates

Revision ID: 003_add_question_bank
Revises: 002_add_analytics
Create Date: 2026-01-03

This migration adds:
- Question templates table for reusable questions
- Tags for categorization
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_add_question_bank'
down_revision: Union[str, None] = '002_add_analytics'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create question bank tables."""
    
    # ============================================
    # Question Templates Table
    # ============================================
    op.create_table(
        'question_templates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('subcategory', sa.String(50), nullable=True),
        sa.Column('difficulty', sa.String(20), default='medium', nullable=True),
        sa.Column('target_roles', sa.JSON(), default=list, nullable=True),
        sa.Column('expected_topics', sa.JSON(), default=list, nullable=True),
        sa.Column('sample_answer', sa.Text(), nullable=True),
        sa.Column('tips', sa.JSON(), default=list, nullable=True),
        sa.Column('time_limit', sa.Integer(), default=120, nullable=True),
        sa.Column('usage_count', sa.Integer(), default=0, nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for efficient querying
    op.create_index('ix_templates_category_difficulty', 'question_templates', ['category', 'difficulty'])
    op.create_index('ix_templates_active', 'question_templates', ['is_active'])
    
    # ============================================
    # Tags Table
    # ============================================
    op.create_table(
        'tags',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('color', sa.String(7), default='#6366f1', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # ============================================
    # Question-Tag Association Table (Many-to-Many)
    # ============================================
    op.create_table(
        'question_template_tags',
        sa.Column('template_id', sa.String(36), sa.ForeignKey('question_templates.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.String(36), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    )
    
    # ============================================
    # Add template reference to interview questions
    # ============================================
    op.add_column('interview_questions',
        sa.Column('template_id', sa.String(36), sa.ForeignKey('question_templates.id', ondelete='SET NULL'), nullable=True)
    )
    op.create_index('ix_questions_template', 'interview_questions', ['template_id'])


def downgrade() -> None:
    """Remove question bank tables."""
    
    # Remove template reference from interview questions
    op.drop_index('ix_questions_template', table_name='interview_questions')
    op.drop_column('interview_questions', 'template_id')
    
    # Drop question-tag association table
    op.drop_table('question_template_tags')
    
    # Drop tags table
    op.drop_table('tags')
    
    # Drop indexes
    op.drop_index('ix_templates_active', table_name='question_templates')
    op.drop_index('ix_templates_category_difficulty', table_name='question_templates')
    
    # Drop question templates table
    op.drop_table('question_templates')
