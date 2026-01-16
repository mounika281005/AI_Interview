"""
==============================================================================
AI Mock Interview System - User Model
==============================================================================

SQLAlchemy model for user profiles in the mock interview system.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional


def utc_now():
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """
    User profile model for the mock interview system.
    
    Stores user information including:
    - Basic profile (name, email, role)
    - Professional details (skills, experience)
    - Interview preferences
    """
    
    __tablename__ = "users"
    
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
    # AUTHENTICATION FIELDS
    # =========================================================================
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # =========================================================================
    # PROFILE FIELDS
    # =========================================================================
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # =========================================================================
    # PROFESSIONAL DETAILS
    # =========================================================================
    # Current/Target job role
    job_role = Column(String(200), nullable=True)
    
    # Skills as JSON array: ["Python", "FastAPI", "Machine Learning"]
    skills = Column(JSON, default=list)
    
    # Years of experience
    experience_years = Column(Integer, default=0)
    
    # Experience level: entry, junior, mid, senior, lead, executive
    experience_level = Column(String(50), default="entry")
    
    # Industry/Domain
    industry = Column(String(200), nullable=True)
    
    # Bio/Summary
    bio = Column(Text, nullable=True)
    
    # Resume/CV URL
    resume_url = Column(String(500), nullable=True)
    
    # LinkedIn profile
    linkedin_url = Column(String(500), nullable=True)
    
    # =========================================================================
    # INTERVIEW PREFERENCES
    # =========================================================================
    # Preferred interview types: ["technical", "behavioral", "mixed"]
    preferred_interview_types = Column(JSON, default=list)
    
    # Difficulty preference: easy, medium, hard
    difficulty_preference = Column(String(50), default="medium")
    
    # Language preference for interviews
    language_preference = Column(String(50), default="en")
    
    # =========================================================================
    # STATISTICS (Aggregated)
    # =========================================================================
    total_interviews = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    best_score = Column(Float, default=0.0)
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    interviews = relationship(
        "InterviewSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def skills_list(self) -> List[str]:
        """Get skills as a list."""
        return self.skills if self.skills else []
    
    def add_skill(self, skill: str) -> None:
        """Add a skill to the user's skill list."""
        if self.skills is None:
            self.skills = []
        if skill not in self.skills:
            self.skills.append(skill)
    
    def update_statistics(self, new_score: float) -> None:
        """Update user statistics after an interview."""
        self.total_interviews += 1
        
        # Update average score
        if self.total_interviews == 1:
            self.average_score = new_score
        else:
            # Incremental average calculation
            self.average_score = (
                (self.average_score * (self.total_interviews - 1) + new_score)
                / self.total_interviews
            )
        
        # Update best score
        if new_score > self.best_score:
            self.best_score = new_score
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"
