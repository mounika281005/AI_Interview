"""
==============================================================================
AI Mock Interview System - Scoring & Feedback Schemas
==============================================================================

Pydantic schemas for Scoring and Feedback API request/response validation.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# SCORING SCHEMAS
# =============================================================================

class ScoringRequest(BaseModel):
    """Schema for calculating final interview scores."""
    session_id: str = Field(..., description="Interview session ID")
    question_scores: List[Dict[str, float]] = Field(
        ..., 
        description="List of scores for each question"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "question_scores": [
                    {"question_id": "q1", "relevance": 85, "grammar": 90, "fluency": 80, "keywords": 75},
                    {"question_id": "q2", "relevance": 78, "grammar": 85, "fluency": 82, "keywords": 80}
                ]
            }
        }
    }


class SectionScore(BaseModel):
    """Schema for a single section score."""
    section_name: str
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    weighted_score: float
    feedback: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "section_name": "Relevance",
                "score": 85.0,
                "weight": 0.35,
                "weighted_score": 29.75,
                "feedback": "Excellent - answers directly address the questions"
            }
        }
    }


class ScoringResponse(BaseModel):
    """Schema for scoring response."""
    success: bool
    session_id: str
    
    # Section-wise scores
    section_scores: List[SectionScore]
    
    # Aggregate scores
    total_score: float = Field(..., ge=0, le=100)
    grade: str
    percentile: Optional[float] = None  # Compared to other users
    
    # Question-level summary
    questions_answered: int
    questions_skipped: int
    best_question_score: float
    worst_question_score: float
    
    # Time analysis
    total_time_seconds: int
    average_time_per_question: float
    
    calculated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "section_scores": [
                    {"section_name": "Relevance", "score": 85.0, "weight": 0.35, "weighted_score": 29.75, "feedback": "Excellent"}
                ],
                "total_score": 82.5,
                "grade": "A",
                "percentile": 78.0,
                "questions_answered": 5,
                "questions_skipped": 0,
                "best_question_score": 92.0,
                "worst_question_score": 68.0,
                "total_time_seconds": 600,
                "average_time_per_question": 120.0,
                "calculated_at": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# FEEDBACK SCHEMAS
# =============================================================================

class FeedbackRequest(BaseModel):
    """Schema for generating feedback."""
    session_id: str = Field(..., description="Interview session ID")
    include_resources: bool = Field(True, description="Include learning resources")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "include_resources": True
            }
        }
    }


class StrengthItem(BaseModel):
    """Schema for a strength item."""
    area: str
    description: str
    examples: List[str] = []
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "area": "Technical Knowledge",
                "description": "Strong understanding of core concepts",
                "examples": ["Clear explanation of ML algorithms", "Accurate use of terminology"]
            }
        }
    }


class WeaknessItem(BaseModel):
    """Schema for a weakness item."""
    area: str
    description: str
    impact: str = Field("medium", description="Impact level: low, medium, high")
    improvement_priority: int = Field(1, ge=1, le=5)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "area": "Communication",
                "description": "Answers could be more structured",
                "impact": "medium",
                "improvement_priority": 2
            }
        }
    }


class SuggestionItem(BaseModel):
    """Schema for an improvement suggestion."""
    priority: int = Field(..., ge=1, le=10)
    category: str
    suggestion: str
    action_items: List[str] = []
    resources: List[Dict[str, str]] = []
    estimated_improvement: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "priority": 1,
                "category": "Communication",
                "suggestion": "Use the STAR method for behavioral questions",
                "action_items": ["Practice structuring answers", "Time yourself"],
                "resources": [{"title": "STAR Method Guide", "url": "https://example.com"}],
                "estimated_improvement": "10-15% score increase"
            }
        }
    }


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    success: bool
    session_id: str
    
    # Performance summary
    performance_rating: str  # excellent, good, average, needs_improvement
    executive_summary: str
    
    # Overall scores
    total_score: float
    grade: str
    
    # Detailed feedback
    strengths: List[StrengthItem]
    weaknesses: List[WeaknessItem]
    suggestions: List[SuggestionItem]
    
    # Question-specific highlights
    best_answer: Optional[Dict[str, Any]] = None
    worst_answer: Optional[Dict[str, Any]] = None
    
    # Readiness assessment
    job_readiness_score: float
    readiness_level: str  # ready, almost_ready, needs_practice, not_ready
    estimated_practice_needed: int  # Number of practice interviews
    
    # Comparison with history
    improvement_percentage: Optional[float] = None
    performance_trend: Optional[str] = None  # improving, stable, declining
    
    # Resources
    recommended_resources: List[Dict[str, str]] = []
    practice_topics: List[str] = []
    
    generated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "performance_rating": "good",
                "executive_summary": "Strong technical performance with room for improvement in communication...",
                "total_score": 82.5,
                "grade": "A",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "job_readiness_score": 75.0,
                "readiness_level": "almost_ready",
                "estimated_practice_needed": 3,
                "improvement_percentage": 8.5,
                "performance_trend": "improving",
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# DASHBOARD / HISTORY SCHEMAS
# =============================================================================

class InterviewHistoryItem(BaseModel):
    """Schema for a single interview in history."""
    session_id: str
    job_role: str
    interview_type: str
    total_score: Optional[float]
    grade: Optional[str]
    status: str
    questions_count: int
    duration_seconds: int
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class InterviewHistoryResponse(BaseModel):
    """Schema for interview history response."""
    user_id: str
    total_interviews: int
    page: int
    page_size: int
    total_pages: int
    interviews: List[InterviewHistoryItem]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_interviews": 15,
                "page": 1,
                "page_size": 10,
                "total_pages": 2,
                "interviews": []
            }
        }
    }


class PerformanceTrend(BaseModel):
    """Schema for performance trend data point."""
    date: str  # ISO date string
    score: float
    interview_type: str
    session_id: str


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics."""
    user_id: str
    
    # Overview stats
    total_interviews: int
    completed_interviews: int
    average_score: float
    best_score: float
    total_practice_hours: float
    
    # Recent performance
    recent_scores: List[PerformanceTrend]
    performance_trend: str  # improving, stable, declining
    improvement_percentage: float
    
    # Category breakdown
    category_scores: Dict[str, float]  # {"technical": 85, "behavioral": 78, ...}
    
    # Skill analysis
    strongest_skills: List[str]
    weakest_skills: List[str]
    
    # Activity
    interviews_this_week: int
    interviews_this_month: int
    current_streak: int  # Days with consecutive practice
    
    # Goals
    target_score: Optional[float] = None
    progress_to_target: Optional[float] = None
    
    generated_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "total_interviews": 25,
                "completed_interviews": 23,
                "average_score": 78.5,
                "best_score": 94.0,
                "total_practice_hours": 12.5,
                "recent_scores": [],
                "performance_trend": "improving",
                "improvement_percentage": 15.2,
                "category_scores": {"technical": 82, "behavioral": 75, "communication": 80},
                "strongest_skills": ["Python", "System Design"],
                "weakest_skills": ["Leadership", "Conflict Resolution"],
                "interviews_this_week": 3,
                "interviews_this_month": 8,
                "current_streak": 5,
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }
    }


class ChartDataResponse(BaseModel):
    """Schema for chart data response."""
    chart_type: str  # line, bar, radar, pie
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "chart_type": "line",
                "title": "Performance Over Time",
                "labels": ["Jan 1", "Jan 8", "Jan 15", "Jan 22"],
                "datasets": [
                    {
                        "label": "Overall Score",
                        "data": [72, 75, 78, 82],
                        "borderColor": "#4CAF50"
                    }
                ]
            }
        }
    }
