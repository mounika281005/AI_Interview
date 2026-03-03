"""
NLP Answer Evaluation Module

A comprehensive NLP-based evaluation system for interview answers.
"""

from .answer_evaluator import (
    AnswerEvaluator,
    EvaluationResult,
    ScoreBreakdown,
    evaluate_answer
)

from .scoring_config import (
    ScoringWeights,
    WeightProfiles,
    EvaluationPreset,
    get_keywords_for_topic,
    get_all_keywords_for_domain,
    get_grade_for_score,
    calculate_weighted_score,
    KEYWORD_DICTIONARIES,
    TRANSITION_WORDS
)

__version__ = "1.0.0"
__author__ = "AI Mock Interview System"

__all__ = [
    # Main evaluator
    "AnswerEvaluator",
    "EvaluationResult",
    "ScoreBreakdown",
    "evaluate_answer",
    
    # Configuration
    "ScoringWeights",
    "WeightProfiles",
    "EvaluationPreset",
    
    # Utilities
    "get_keywords_for_topic",
    "get_all_keywords_for_domain",
    "get_grade_for_score",
    "calculate_weighted_score",
    
    # Data
    "KEYWORD_DICTIONARIES",
    "TRANSITION_WORDS",
]
