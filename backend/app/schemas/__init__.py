"""
==============================================================================
AI Mock Interview System - Schemas Package
==============================================================================

This package exports all Pydantic schemas for API validation.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    UserStatsResponse,
    Token,
    TokenPayload,
)

# Interview schemas
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionUpdate,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
    InterviewQuestionResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    GeneratedQuestion,
    AudioUploadResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    EvaluationRequest,
    EvaluationScores,
    EvaluationResponse,
)

# Feedback & Scoring schemas
from app.schemas.feedback import (
    ScoringRequest,
    ScoringResponse,
    SectionScore,
    FeedbackRequest,
    FeedbackResponse,
    StrengthItem,
    WeaknessItem,
    SuggestionItem,
    InterviewHistoryItem,
    InterviewHistoryResponse,
    PerformanceTrend,
    DashboardStatsResponse,
    ChartDataResponse,
)

# Common schemas
from app.schemas.common import (
    APIResponse,
    ErrorResponse,
    ValidationErrorResponse,
    PaginationParams,
    PaginatedResponse,
    HealthCheckResponse,
    FileUploadResponse,
    SortParams,
    DateRangeFilter,
    SearchParams,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserResponse",
    "UserProfileResponse",
    "UserStatsResponse",
    "Token",
    "TokenPayload",
    
    # Interview
    "InterviewSessionCreate",
    "InterviewSessionUpdate",
    "InterviewSessionResponse",
    "InterviewSessionDetailResponse",
    "InterviewQuestionResponse",
    "QuestionGenerationRequest",
    "QuestionGenerationResponse",
    "GeneratedQuestion",
    "AudioUploadResponse",
    "TranscriptionRequest",
    "TranscriptionResponse",
    "EvaluationRequest",
    "EvaluationScores",
    "EvaluationResponse",
    
    # Feedback & Scoring
    "ScoringRequest",
    "ScoringResponse",
    "SectionScore",
    "FeedbackRequest",
    "FeedbackResponse",
    "StrengthItem",
    "WeaknessItem",
    "SuggestionItem",
    "InterviewHistoryItem",
    "InterviewHistoryResponse",
    "PerformanceTrend",
    "DashboardStatsResponse",
    "ChartDataResponse",
    
    # Common
    "APIResponse",
    "ErrorResponse",
    "ValidationErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "HealthCheckResponse",
    "FileUploadResponse",
    "SortParams",
    "DateRangeFilter",
    "SearchParams",
]
