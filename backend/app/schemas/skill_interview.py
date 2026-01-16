"""
==============================================================================
AI Mock Interview System - Skill-Based Interview Schemas
==============================================================================

Pydantic schemas for the streamlined skill-based interview flow.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# TECHNOLOGY/SKILL SCHEMAS
# =============================================================================

class Technology(BaseModel):
    """Schema for a technology/skill option."""
    id: str
    name: str
    category: str
    icon: Optional[str] = None
    description: Optional[str] = None


class TechnologyListResponse(BaseModel):
    """Schema for list of available technologies."""
    technologies: List[Technology]
    categories: List[str]


# =============================================================================
# QUESTION GENERATION SCHEMAS
# =============================================================================

class SkillInterviewRequest(BaseModel):
    """Request to start a skill-based interview."""
    technology: str = Field(..., min_length=1, max_length=100, description="Selected technology/skill")
    num_questions: int = Field(default=5, ge=1, le=10, description="Number of questions")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "technology": "Python",
                "num_questions": 5,
                "difficulty": "medium"
            }
        }
    }


class SkillQuestion(BaseModel):
    """Schema for a single skill-based question."""
    id: str
    question_number: int
    question_text: str
    technology: str
    difficulty: str
    expected_keywords: List[str] = []
    ideal_answer: Optional[str] = None
    time_limit_seconds: int = 120
    
    model_config = {"from_attributes": True}


class SkillInterviewResponse(BaseModel):
    """Response after creating a skill interview session."""
    session_id: str
    technology: str
    difficulty: str
    total_questions: int
    questions: List[SkillQuestion]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# =============================================================================
# AUDIO SUBMISSION SCHEMAS
# =============================================================================

class AudioSubmission(BaseModel):
    """Schema for audio submission info."""
    question_id: str
    audio_duration_seconds: float
    file_size_bytes: int


class SubmitInterviewRequest(BaseModel):
    """Request to submit all answers for evaluation."""
    session_id: str
    answers: List[AudioSubmission]


# =============================================================================
# SCORING & EVALUATION SCHEMAS
# =============================================================================

class QuestionScore(BaseModel):
    """Detailed score for a single question."""
    question_id: str
    question_number: int
    question_text: str
    
    # User's answer
    transcript: str
    
    # Individual scores (0-5 scale)
    grammar_score: float = Field(..., ge=0, le=5)
    fluency_score: float = Field(..., ge=0, le=5)
    structure_score: float = Field(..., ge=0, le=5)
    similarity_score: float = Field(..., ge=0, le=5)
    
    # Overall score for this question
    overall_score: float = Field(..., ge=0, le=5)
    
    # Feedback
    strengths: List[str] = []
    improvements: List[str] = []
    ideal_answer: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "q-001",
                "question_number": 1,
                "question_text": "What is Python?",
                "transcript": "Python is a high-level programming language...",
                "grammar_score": 4.5,
                "fluency_score": 4.0,
                "structure_score": 3.5,
                "similarity_score": 4.2,
                "overall_score": 4.1,
                "strengths": ["Good technical accuracy", "Clear explanation"],
                "improvements": ["Could include more examples", "Mention use cases"],
                "ideal_answer": "Python is a high-level, interpreted programming language..."
            }
        }
    }


class InterviewResult(BaseModel):
    """Complete interview result with all scores."""
    session_id: str
    technology: str
    difficulty: str
    
    # Question-wise scores
    question_scores: List[QuestionScore]
    
    # Aggregate scores (0-5 scale)
    total_grammar_score: float
    total_fluency_score: float
    total_structure_score: float
    total_similarity_score: float
    
    # Final total score (sum of all question scores)
    total_score: float
    max_possible_score: float
    percentage_score: float
    
    # Overall performance
    grade: str
    performance_summary: str
    
    # Overall feedback
    overall_strengths: List[str] = []
    overall_improvements: List[str] = []
    
    completed_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "sess-001",
                "technology": "Python",
                "difficulty": "medium",
                "question_scores": [],
                "total_grammar_score": 22.5,
                "total_fluency_score": 20.0,
                "total_structure_score": 18.5,
                "total_similarity_score": 21.0,
                "total_score": 20.5,
                "max_possible_score": 25.0,
                "percentage_score": 82.0,
                "grade": "A",
                "performance_summary": "Excellent performance with strong technical knowledge",
                "overall_strengths": ["Strong technical vocabulary"],
                "overall_improvements": ["Work on answer structure"],
                "completed_at": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# HISTORY & STORAGE SCHEMAS
# =============================================================================

class InterviewHistoryItem(BaseModel):
    """Schema for an interview in history."""
    session_id: str
    technology: str
    difficulty: str
    total_questions: int
    total_score: float
    max_possible_score: float
    percentage_score: float
    grade: str
    completed_at: datetime
    
    model_config = {"from_attributes": True}


class InterviewHistoryResponse(BaseModel):
    """Response for interview history."""
    interviews: List[InterviewHistoryItem]
    total_count: int
