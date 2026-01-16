"""
==============================================================================
AI Mock Interview System - Interview Schemas
==============================================================================

Pydantic schemas for Interview Session API request/response validation.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class InterviewSessionCreate(BaseModel):
    """Schema for creating a new interview session."""
    job_role: str = Field(..., min_length=1, max_length=200, description="Target job role")
    interview_type: str = Field("technical", description="Type: technical, behavioral, mixed")
    skills_tested: List[str] = Field(default_factory=list, description="Skills to focus on")
    experience_level: str = Field("mid", description="Experience level: entry, junior, mid, senior")
    difficulty: str = Field("medium", description="Difficulty: easy, medium, hard")
    total_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    time_limit_per_question: int = Field(180, ge=30, le=600, description="Seconds per question")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "job_role": "Senior Python Developer",
                "interview_type": "technical",
                "skills_tested": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "experience_level": "senior",
                "difficulty": "hard",
                "total_questions": 5,
                "time_limit_per_question": 180
            }
        }
    }


class InterviewSessionUpdate(BaseModel):
    """Schema for updating interview session."""
    status: Optional[str] = None
    current_question_index: Optional[int] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in_progress",
                "current_question_index": 2
            }
        }
    }


# =============================================================================
# QUESTION SCHEMAS
# =============================================================================

class QuestionGenerationRequest(BaseModel):
    """Schema for requesting AI-generated questions."""
    job_role: str = Field(..., description="Target job role")
    skills: List[str] = Field(..., min_length=1, description="Skills to test")
    experience_level: str = Field("mid", description="Experience level")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    interview_type: str = Field("technical", description="Type: technical, behavioral, mixed")
    difficulty: str = Field("medium", description="Difficulty level")
    
    # Optional customization
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")
    avoid_topics: Optional[List[str]] = Field(None, description="Topics to avoid")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "job_role": "Machine Learning Engineer",
                "skills": ["Python", "TensorFlow", "NLP", "Deep Learning"],
                "experience_level": "senior",
                "num_questions": 5,
                "interview_type": "technical",
                "difficulty": "hard",
                "focus_areas": ["System Design", "Model Optimization"]
            }
        }
    }


class GeneratedQuestion(BaseModel):
    """Schema for a single generated question."""
    question_text: str
    category: str
    difficulty: str
    expected_keywords: List[str]
    ideal_answer: Optional[str] = None
    time_limit: int = 180
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question_text": "Explain the difference between supervised and unsupervised learning with examples.",
                "category": "Machine Learning Fundamentals",
                "difficulty": "medium",
                "expected_keywords": ["supervised", "unsupervised", "classification", "clustering", "labeled data"],
                "ideal_answer": "Supervised learning uses labeled data...",
                "time_limit": 180
            }
        }
    }


class QuestionGenerationResponse(BaseModel):
    """Schema for question generation response."""
    session_id: str
    job_role: str
    questions: List[GeneratedQuestion]
    generated_at: datetime
    ai_model_used: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_role": "Machine Learning Engineer",
                "questions": [],
                "generated_at": "2024-01-15T10:30:00Z",
                "ai_model_used": "gpt-4-turbo"
            }
        }
    }


# =============================================================================
# AUDIO UPLOAD SCHEMAS
# =============================================================================

class AudioUploadResponse(BaseModel):
    """Schema for audio upload response."""
    success: bool
    message: str
    question_id: str
    file_path: str
    file_size: int
    duration_seconds: Optional[float] = None
    uploaded_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Audio uploaded successfully",
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "file_path": "/uploads/audio/question_123.wav",
                "file_size": 1024000,
                "duration_seconds": 45.5,
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# SPEECH-TO-TEXT SCHEMAS
# =============================================================================

class TranscriptionRequest(BaseModel):
    """Schema for transcription request."""
    question_id: str = Field(..., description="Question ID with audio to transcribe")
    language: str = Field("en", description="Language code")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "language": "en"
            }
        }
    }


class TranscriptionResponse(BaseModel):
    """Schema for speech-to-text response."""
    success: bool
    question_id: str
    transcript: str
    confidence: Optional[float] = None
    language_detected: Optional[str] = None
    duration_seconds: Optional[float] = None
    word_count: int
    processing_time_ms: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "transcript": "Machine learning is a subset of artificial intelligence...",
                "confidence": 0.95,
                "language_detected": "en",
                "duration_seconds": 45.5,
                "word_count": 150,
                "processing_time_ms": 2500
            }
        }
    }


# =============================================================================
# EVALUATION SCHEMAS
# =============================================================================

class EvaluationRequest(BaseModel):
    """Schema for NLP evaluation request."""
    question_id: str = Field(..., description="Question ID to evaluate")
    question_text: str = Field(..., description="The interview question")
    transcript: str = Field(..., description="User's answer transcript")
    expected_keywords: List[str] = Field(default_factory=list, description="Expected keywords")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "question_text": "What is machine learning?",
                "transcript": "Machine learning is a subset of AI that enables systems to learn...",
                "expected_keywords": ["AI", "algorithm", "data", "training", "model"]
            }
        }
    }


class EvaluationScores(BaseModel):
    """Schema for evaluation scores."""
    relevance_score: float = Field(..., ge=0, le=100)
    grammar_score: float = Field(..., ge=0, le=100)
    fluency_score: float = Field(..., ge=0, le=100)
    keyword_score: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "relevance_score": 85.0,
                "grammar_score": 90.0,
                "fluency_score": 80.0,
                "keyword_score": 75.0,
                "overall_score": 82.5
            }
        }
    }


class EvaluationResponse(BaseModel):
    """Schema for NLP evaluation response."""
    success: bool
    question_id: str
    scores: EvaluationScores
    grade: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    feedback_text: str
    evaluation_time_ms: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "scores": {
                    "relevance_score": 85.0,
                    "grammar_score": 90.0,
                    "fluency_score": 80.0,
                    "keyword_score": 75.0,
                    "overall_score": 82.5
                },
                "grade": "A",
                "strengths": ["Clear explanation", "Good examples"],
                "weaknesses": ["Missing some key terms"],
                "suggestions": ["Include more technical vocabulary"],
                "feedback_text": "Good answer with clear structure...",
                "evaluation_time_ms": 500
            }
        }
    }


# =============================================================================
# SESSION RESPONSE SCHEMAS
# =============================================================================

class InterviewQuestionResponse(BaseModel):
    """Schema for interview question in response."""
    id: str
    question_text: str
    question_order: int
    category: Optional[str] = None
    difficulty: str
    time_limit: int
    has_response: bool
    is_evaluated: bool
    overall_score: Optional[float] = None
    
    model_config = {"from_attributes": True}


class InterviewSessionResponse(BaseModel):
    """Schema for interview session response."""
    id: str
    user_id: str
    job_role: str
    interview_type: str
    skills_tested: List[str]
    experience_level: str
    difficulty: str
    total_questions: int
    current_question_index: int
    status: str
    overall_score: Optional[float] = None
    grade: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: int
    created_at: datetime
    
    # Questions summary
    questions: List[InterviewQuestionResponse] = []
    
    model_config = {"from_attributes": True}


class InterviewSessionDetailResponse(InterviewSessionResponse):
    """Detailed session response with full question data."""
    relevance_score: Optional[float] = None
    grammar_score: Optional[float] = None
    fluency_score: Optional[float] = None
    technical_score: Optional[float] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    summary: Optional[str] = None
    
    model_config = {"from_attributes": True}
