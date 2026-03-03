"""
==============================================================================
AI Mock Interview System - User Schemas
==============================================================================

Pydantic schemas for User API request/response validation.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    """Base schema with common user fields."""
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    
    # Optional profile fields
    phone: Optional[str] = Field(None, max_length=20)
    job_role: Optional[str] = Field(None, max_length=200)
    skills: Optional[List[str]] = Field(default_factory=list)
    experience_years: Optional[int] = Field(0, ge=0, le=50)
    experience_level: Optional[str] = Field("entry")
    industry: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    
    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v: str) -> str:
        allowed = ["entry", "junior", "mid", "senior", "lead", "executive"]
        if v and v.lower() not in allowed:
            raise ValueError(f"Experience level must be one of: {allowed}")
        return v.lower() if v else "entry"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john.doe@example.com",
                "password": "securePassword123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "job_role": "Software Engineer",
                "skills": ["Python", "FastAPI", "Machine Learning"],
                "experience_years": 3,
                "experience_level": "mid",
                "industry": "Technology",
                "bio": "Passionate developer with focus on AI/ML"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    job_role: Optional[str] = Field(None, max_length=200)
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    experience_level: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    resume_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    preferred_interview_types: Optional[List[str]] = None
    difficulty_preference: Optional[str] = None
    language_preference: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "job_role": "Senior Software Engineer",
                "skills": ["Python", "FastAPI", "Machine Learning", "Docker"],
                "experience_years": 5,
                "experience_level": "senior"
            }
        }
    }


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "john.doe@example.com",
                "password": "securePassword123"
            }
        }
    }


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class UserResponse(UserBase):
    """Schema for user response (public profile)."""
    id: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    job_role: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    experience_level: str = "entry"
    industry: Optional[str] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Statistics
    total_interviews: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    
    # Timestamps
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1-555-123-4567",
                "job_role": "Software Engineer",
                "skills": ["Python", "FastAPI", "Machine Learning"],
                "experience_years": 3,
                "experience_level": "mid",
                "industry": "Technology",
                "bio": "Passionate developer",
                "total_interviews": 15,
                "average_score": 78.5,
                "best_score": 92.0,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
    }


class UserProfileResponse(UserResponse):
    """Extended user profile with additional details."""
    resume_url: Optional[str] = None
    preferred_interview_types: List[str] = []
    difficulty_preference: str = "medium"
    language_preference: str = "en"
    is_verified: bool = False
    
    model_config = {"from_attributes": True}


class UserStatsResponse(BaseModel):
    """Schema for user statistics."""
    user_id: str
    total_interviews: int
    completed_interviews: int
    average_score: float
    best_score: float
    improvement_trend: float  # Percentage improvement over last 5 interviews
    strengths: List[str]
    areas_to_improve: List[str]
    interview_history_summary: dict
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_interviews": 15,
                "completed_interviews": 14,
                "average_score": 78.5,
                "best_score": 92.0,
                "improvement_trend": 12.5,
                "strengths": ["Technical knowledge", "Problem solving"],
                "areas_to_improve": ["Communication", "Time management"],
                "interview_history_summary": {
                    "last_7_days": 3,
                    "last_30_days": 8
                }
            }
        }
    }


# =============================================================================
# AUTHENTICATION SCHEMAS
# =============================================================================

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            }
        }
    }


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: str  # User ID
    exp: datetime
    iat: datetime
