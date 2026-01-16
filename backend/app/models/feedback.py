"""
==============================================================================
AI Mock Interview System - Feedback Model
==============================================================================

SQLAlchemy model for storing aggregated feedback and improvement tracking.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import uuid
from datetime import datetime, timezone


def utc_now():
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


class InterviewFeedback(Base):
    """
    Aggregated feedback model for interview sessions.
    
    Stores detailed feedback analysis including:
    - Performance summary
    - Strengths and weaknesses
    - Improvement recommendations
    - Comparison with previous interviews
    """
    
    __tablename__ = "interview_feedback"
    
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
        unique=True,  # One feedback per session
        index=True
    )
    
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # =========================================================================
    # PERFORMANCE SUMMARY
    # =========================================================================
    # Overall performance rating: excellent, good, average, needs_improvement
    performance_rating = Column(String(50), nullable=True)
    
    # Executive summary (AI-generated)
    executive_summary = Column(Text, nullable=True)
    
    # =========================================================================
    # DETAILED SCORES
    # =========================================================================
    # Category-wise scores (0-100)
    communication_score = Column(Float, nullable=True)
    technical_knowledge_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    structure_score = Column(Float, nullable=True)
    
    # =========================================================================
    # STRENGTHS ANALYSIS
    # =========================================================================
    # Top strengths as JSON array
    # Format: [{"area": "Technical", "description": "...", "examples": [...]}]
    strengths = Column(JSON, default=list)
    
    # Strongest skill areas
    strongest_areas = Column(JSON, default=list)
    
    # =========================================================================
    # WEAKNESSES ANALYSIS
    # =========================================================================
    # Areas for improvement as JSON array
    # Format: [{"area": "Communication", "description": "...", "impact": "high"}]
    weaknesses = Column(JSON, default=list)
    
    # Weakest skill areas
    weakest_areas = Column(JSON, default=list)
    
    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================
    # Improvement suggestions
    # Format: [{"priority": 1, "suggestion": "...", "resources": [...]}]
    improvement_suggestions = Column(JSON, default=list)
    
    # Recommended resources (courses, articles, etc.)
    recommended_resources = Column(JSON, default=list)
    
    # Practice topics
    practice_topics = Column(JSON, default=list)
    
    # =========================================================================
    # COMPARISON WITH HISTORY
    # =========================================================================
    # Improvement compared to last interview (percentage)
    improvement_percentage = Column(Float, nullable=True)
    
    # Trend: improving, stable, declining
    performance_trend = Column(String(50), nullable=True)
    
    # Comparison details
    comparison_details = Column(JSON, nullable=True)
    
    # =========================================================================
    # INTERVIEW-SPECIFIC FEEDBACK
    # =========================================================================
    # Best answered question
    best_answer_question_id = Column(String(36), nullable=True)
    best_answer_feedback = Column(Text, nullable=True)
    
    # Worst answered question
    worst_answer_question_id = Column(String(36), nullable=True)
    worst_answer_feedback = Column(Text, nullable=True)
    
    # =========================================================================
    # READINESS ASSESSMENT
    # =========================================================================
    # Job readiness score (0-100)
    job_readiness_score = Column(Float, nullable=True)
    
    # Readiness level: not_ready, needs_practice, almost_ready, ready
    readiness_level = Column(String(50), nullable=True)
    
    # Estimated interviews needed to be job-ready
    estimated_practice_needed = Column(Integer, nullable=True)
    
    # =========================================================================
    # METADATA
    # =========================================================================
    # Feedback generation metadata
    generated_by = Column(String(100), default="ai")  # ai, manual, hybrid
    ai_model_used = Column(String(100), nullable=True)
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def add_strength(self, area: str, description: str, examples: list = None) -> None:
        """Add a strength to the feedback."""
        if self.strengths is None:
            self.strengths = []
        
        self.strengths.append({
            "area": area,
            "description": description,
            "examples": examples or []
        })
    
    def add_weakness(self, area: str, description: str, impact: str = "medium") -> None:
        """Add a weakness to the feedback."""
        if self.weaknesses is None:
            self.weaknesses = []
        
        self.weaknesses.append({
            "area": area,
            "description": description,
            "impact": impact
        })
    
    def add_suggestion(
        self,
        suggestion: str,
        priority: int = 1,
        resources: list = None
    ) -> None:
        """Add an improvement suggestion."""
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []
        
        self.improvement_suggestions.append({
            "priority": priority,
            "suggestion": suggestion,
            "resources": resources or []
        })
    
    def calculate_readiness(self) -> str:
        """Calculate and set job readiness level."""
        if self.job_readiness_score is None:
            return "unknown"
        
        if self.job_readiness_score >= 80:
            self.readiness_level = "ready"
            self.estimated_practice_needed = 0
        elif self.job_readiness_score >= 65:
            self.readiness_level = "almost_ready"
            self.estimated_practice_needed = 2
        elif self.job_readiness_score >= 50:
            self.readiness_level = "needs_practice"
            self.estimated_practice_needed = 5
        else:
            self.readiness_level = "not_ready"
            self.estimated_practice_needed = 10
        
        return self.readiness_level
    
    def __repr__(self) -> str:
        return f"<InterviewFeedback(id={self.id}, session={self.session_id}, rating={self.performance_rating})>"
