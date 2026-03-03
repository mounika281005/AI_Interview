"""
==============================================================================
AI Mock Interview System - Services Package
==============================================================================

Exports all service classes and functions.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

# Authentication Service
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    get_optional_user,
    security
)

# Question Generation Service
from app.services.question_service import (
    QuestionGeneratorService,
    GeneratedQuestion,
    get_question_service
)

# Speech-to-Text Service
from app.services.stt_service import (
    SpeechToTextService,
    TranscriptionResult,
    get_stt_service
)

# NLP Evaluation Service
from app.services.evaluation_service import (
    NLPEvaluationService,
    EvaluationScore,
    EvaluationResult,
    get_evaluation_service
)

# Scoring Service
from app.services.scoring_service import (
    ScoringService,
    ScoringWeights,
    ScoreBreakdown,
    QuestionScore,
    SessionScore,
    get_scoring_service
)

# Feedback Service
from app.services.feedback_service import (
    FeedbackService,
    FeedbackItem,
    ResourceRecommendation,
    InterviewFeedbackResult,
    get_feedback_service
)

# Statistics Service
from app.services.stats_service import (
    StatsService,
    UserStats,
    PerformanceTrend,
    ChartData,
    calculate_user_stats,
    get_stats_service
)


__all__ = [
    # Auth
    'get_password_hash',
    'verify_password',
    'create_access_token',
    'verify_token',
    'get_current_user',
    'get_current_active_user',
    'get_optional_user',
    'security',
    
    # Question Generation
    'QuestionGeneratorService',
    'GeneratedQuestion',
    'get_question_service',
    
    # Speech-to-Text
    'SpeechToTextService',
    'TranscriptionResult',
    'get_stt_service',
    
    # Evaluation
    'NLPEvaluationService',
    'EvaluationScore',
    'EvaluationResult',
    'get_evaluation_service',
    
    # Scoring
    'ScoringService',
    'ScoringWeights',
    'ScoreBreakdown',
    'QuestionScore',
    'SessionScore',
    'get_scoring_service',
    
    # Feedback
    'FeedbackService',
    'FeedbackItem',
    'ResourceRecommendation',
    'InterviewFeedbackResult',
    'get_feedback_service',
    
    # Statistics
    'StatsService',
    'UserStats',
    'PerformanceTrend',
    'ChartData',
    'calculate_user_stats',
    'get_stats_service',
]
