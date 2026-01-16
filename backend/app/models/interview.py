"""
==============================================================================
AI Mock Interview System - Interview Session Model
==============================================================================

SQLAlchemy model for interview sessions, tracking the complete interview
flow from question generation to final scoring.

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
    DateTime, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class InterviewStatus(str, enum.Enum):
    """Interview session status."""
    CREATED = "created"           # Session created, not started
    IN_PROGRESS = "in_progress"   # Interview ongoing
    COMPLETED = "completed"       # All questions answered
    EVALUATED = "evaluated"       # Scores calculated
    CANCELLED = "cancelled"       # Session cancelled


class InterviewType(str, enum.Enum):
    """Type of interview."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"


class InterviewSession(Base):
    """
    Interview session model.
    
    Represents a complete interview session including:
    - Session metadata (type, role, duration)
    - Questions and answers
    - Scores and feedback
    """
    
    __tablename__ = "interview_sessions"
    
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
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # =========================================================================
    # SESSION METADATA
    # =========================================================================
    # Interview type
    interview_type = Column(String(50), default=InterviewType.TECHNICAL.value)
    
    # Target job role for this interview
    job_role = Column(String(200), nullable=False)
    
    # Skills being tested
    skills_tested = Column(JSON, default=list)
    
    # Experience level for question difficulty
    experience_level = Column(String(50), default="mid")
    
    # Difficulty: easy, medium, hard
    difficulty = Column(String(50), default="medium")
    
    # Number of questions in this session
    total_questions = Column(Integer, default=5)
    
    # Current question index (0-based)
    current_question_index = Column(Integer, default=0)
    
    # Session status
    status = Column(String(50), default=InterviewStatus.CREATED.value)
    
    # =========================================================================
    # TIMING
    # =========================================================================
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Total duration in seconds
    duration_seconds = Column(Integer, default=0)
    
    # Time limit per question (seconds)
    time_limit_per_question = Column(Integer, default=180)  # 3 minutes default
    
    # =========================================================================
    # SCORES (Aggregated)
    # =========================================================================
    # Overall interview score (0-100)
    overall_score = Column(Float, nullable=True)
    
    # Section-wise scores
    relevance_score = Column(Float, nullable=True)
    grammar_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    
    # Letter grade
    grade = Column(String(5), nullable=True)
    
    # =========================================================================
    # FEEDBACK (Aggregated)
    # =========================================================================
    # Overall strengths identified
    strengths = Column(JSON, default=list)
    
    # Areas for improvement
    weaknesses = Column(JSON, default=list)
    
    # Improvement suggestions
    suggestions = Column(JSON, default=list)
    
    # AI-generated summary
    summary = Column(Text, nullable=True)
    
    # =========================================================================
    # SETTINGS
    # =========================================================================
    # Session configuration as JSON
    settings = Column(JSON, default=dict)
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    user = relationship("User", back_populates="interviews")
    
    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.question_order"
    )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def start_interview(self) -> None:
        """Mark interview as started."""
        self.status = InterviewStatus.IN_PROGRESS.value
        self.started_at = utc_now()

    def complete_interview(self) -> None:
        """Mark interview as completed."""
        self.status = InterviewStatus.COMPLETED.value
        self.completed_at = utc_now()
        
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
    
    def calculate_overall_score(self) -> float:
        """Calculate overall score from section scores."""
        scores = [
            s for s in [
                self.relevance_score,
                self.grammar_score,
                self.fluency_score,
                self.technical_score
            ]
            if s is not None
        ]
        
        if scores:
            self.overall_score = sum(scores) / len(scores)
            self.grade = self._get_grade(self.overall_score)
        
        return self.overall_score
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    @property
    def is_complete(self) -> bool:
        """Check if interview is complete."""
        return self.status in [
            InterviewStatus.COMPLETED.value,
            InterviewStatus.EVALUATED.value
        ]
    
    @property
    def progress_percentage(self) -> float:
        """Get interview progress as percentage."""
        if self.total_questions == 0:
            return 0.0
        return (self.current_question_index / self.total_questions) * 100
    
    def __repr__(self) -> str:
        return f"<InterviewSession(id={self.id}, role={self.job_role}, status={self.status})>"
