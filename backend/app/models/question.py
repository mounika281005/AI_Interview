"""
==============================================================================
AI Mock Interview System - Interview Question Model
==============================================================================

SQLAlchemy model for individual interview questions within a session,
including audio responses, transcripts, and evaluation scores.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


def utc_now():
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


class InterviewQuestion(Base):
    """
    Individual interview question model.
    
    Stores:
    - Question text and metadata
    - User's audio response
    - Speech-to-text transcript
    - NLP evaluation scores
    """
    
    __tablename__ = "interview_questions"
    
    # =========================================================================
    # PRIMARY KEY
    # =========================================================================
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # =========================================================================
    # FOREIGN KEYS
    # =========================================================================
    session_id = Column(
        String(36),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # =========================================================================
    # QUESTION DETAILS
    # =========================================================================
    # Question text
    question_text = Column(Text, nullable=False)
    
    # Question order within session (1-based)
    question_order = Column(Integer, nullable=False)
    
    # Question category: technical, behavioral, situational, etc.
    category = Column(String(100), nullable=True)
    
    # Difficulty level: easy, medium, hard
    difficulty = Column(String(50), default="medium")
    
    # Expected keywords for evaluation
    expected_keywords = Column(JSON, default=list)
    
    # Ideal answer (for reference/comparison)
    ideal_answer = Column(Text, nullable=True)
    
    # Time allocated for this question (seconds)
    time_limit = Column(Integer, default=180)
    
    # =========================================================================
    # USER RESPONSE
    # =========================================================================
    # Audio file path (stored locally or cloud URL)
    audio_file_path = Column(String(500), nullable=True)
    
    # Audio file size in bytes
    audio_file_size = Column(Integer, nullable=True)
    
    # Audio duration in seconds
    audio_duration_seconds = Column(Float, nullable=True)
    
    # Transcript from speech-to-text
    transcript = Column(Text, nullable=True)
    
    # STT confidence score (0-1)
    transcript_confidence = Column(Float, nullable=True)
    
    # Time taken to answer (seconds)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Was the question skipped?
    is_skipped = Column(Boolean, default=False)
    
    # =========================================================================
    # EVALUATION SCORES
    # =========================================================================
    # Has this question been evaluated?
    is_evaluated = Column(Boolean, default=False)
    
    # Individual scores (0-100)
    relevance_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    keyword_score = Column(Float, nullable=True)
    
    # Overall score for this question (0-100)
    overall_score = Column(Float, nullable=True)
    
    # =========================================================================
    # FEEDBACK
    # =========================================================================
    # Strengths for this answer
    strengths = Column(JSON, default=list)
    
    # Areas for improvement
    weaknesses = Column(JSON, default=list)
    
    # Specific suggestions
    suggestions = Column(JSON, default=list)
    
    # Detailed evaluation feedback
    feedback_text = Column(Text, nullable=True)
    
    # =========================================================================
    # METADATA
    # =========================================================================
    # Raw evaluation data from NLP module
    evaluation_raw = Column(JSON, nullable=True)
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    session = relationship("InterviewSession", back_populates="questions")
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def set_audio_response(
        self,
        file_path: str,
        file_size: int,
        duration: float
    ) -> None:
        """Set audio response details."""
        self.audio_file_path = file_path
        self.audio_file_size = file_size
        self.audio_duration_seconds = duration
        self.answered_at = utc_now()
    
    def set_transcript(self, transcript: str, confidence: float = None) -> None:
        """Set speech-to-text transcript."""
        self.transcript = transcript
        if confidence is not None:
            self.transcript_confidence = confidence
    
    def set_evaluation(
        self,
        relevance: float,
        grammar: float,
        fluency: float,
        keywords: float,
        strengths: list = None,
        weaknesses: list = None,
        suggestions: list = None,
        feedback: str = None,
        raw_data: dict = None
    ) -> None:
        """Set evaluation scores and feedback."""
        self.relevance_score = relevance
        self.grammar_score = grammar
        self.fluency_score = fluency
        self.keyword_score = keywords
        
        # Calculate overall score (weighted average)
        self.overall_score = (
            relevance * 0.35 +
            grammar * 0.20 +
            fluency * 0.25 +
            keywords * 0.20
        )
        
        if strengths:
            self.strengths = strengths
        if weaknesses:
            self.weaknesses = weaknesses
        if suggestions:
            self.suggestions = suggestions
        if feedback:
            self.feedback_text = feedback
        if raw_data:
            self.evaluation_raw = raw_data
        
        self.is_evaluated = True
        self.evaluated_at = utc_now()
    
    def skip_question(self) -> None:
        """Mark question as skipped."""
        self.is_skipped = True
        self.overall_score = 0.0
        self.relevance_score = 0.0
        self.grammar_score = 0.0
        self.fluency_score = 0.0
        self.keyword_score = 0.0
        self.feedback_text = "Question was skipped."
        self.is_evaluated = True
    
    @property
    def has_response(self) -> bool:
        """Check if question has an audio response."""
        return self.audio_file_path is not None or self.transcript is not None
    
    @property
    def word_count(self) -> int:
        """Get word count of transcript."""
        if self.transcript:
            return len(self.transcript.split())
        return 0
    
    def __repr__(self) -> str:
        return f"<InterviewQuestion(id={self.id}, order={self.question_order}, score={self.overall_score})>"
