"""
==============================================================================
AI Mock Interview System - Scoring Service
==============================================================================

Calculates final scores from NLP evaluation metrics with configurable weights.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# SCORING CONFIGURATION
# =============================================================================

@dataclass
class ScoringWeights:
    """Configurable weights for score calculation."""
    relevance: float = 0.35
    grammar: float = 0.20
    fluency: float = 0.25
    keyword_usage: float = 0.20
    
    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = self.relevance + self.grammar + self.fluency + self.keyword_usage
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, normalizing...")
            self.relevance /= total
            self.grammar /= total
            self.fluency /= total
            self.keyword_usage /= total


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown."""
    relevance_score: float
    grammar_score: float
    fluency_score: float
    keyword_score: float
    weighted_relevance: float
    weighted_grammar: float
    weighted_fluency: float
    weighted_keyword: float
    total_score: float
    letter_grade: str
    percentile: Optional[int] = None


@dataclass
class QuestionScore:
    """Score for a single question."""
    question_id: str
    question_number: int
    scores: ScoreBreakdown
    time_taken: int
    response_length: int


@dataclass
class SessionScore:
    """Complete session scoring result."""
    session_id: str
    question_scores: List[QuestionScore]
    average_scores: ScoreBreakdown
    total_score: float
    letter_grade: str
    performance_summary: str
    score_trends: Dict[str, List[float]]


# =============================================================================
# SCORING SERVICE
# =============================================================================

class ScoringService:
    """
    Service for calculating interview scores.
    
    Features:
    - Configurable metric weights
    - Letter grade assignment
    - Percentile calculation
    - Score trend analysis
    
    Usage:
        scorer = ScoringService()
        final_score = scorer.calculate_final_score(
            relevance=85,
            grammar=78,
            fluency=82,
            keyword_usage=90
        )
    """
    
    # Grade thresholds
    GRADE_THRESHOLDS = [
        (90, 'A+'),
        (85, 'A'),
        (80, 'A-'),
        (75, 'B+'),
        (70, 'B'),
        (65, 'B-'),
        (60, 'C+'),
        (55, 'C'),
        (50, 'C-'),
        (45, 'D+'),
        (40, 'D'),
        (0, 'F')
    ]
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize scoring service.
        
        Args:
            weights: Custom scoring weights (optional)
        """
        self.weights = weights or ScoringWeights()
        logger.info(f"Scoring service initialized with weights: {self.weights}")
    
    def calculate_final_score(
        self,
        relevance: float,
        grammar: float,
        fluency: float,
        keyword_usage: float
    ) -> ScoreBreakdown:
        """
        Calculate final weighted score from individual metrics.
        
        Args:
            relevance: Relevance score (0-100)
            grammar: Grammar score (0-100)
            fluency: Fluency score (0-100)
            keyword_usage: Keyword usage score (0-100)
        
        Returns:
            ScoreBreakdown with detailed scores
        """
        # Validate inputs
        scores = [relevance, grammar, fluency, keyword_usage]
        scores = [max(0, min(100, s)) for s in scores]
        relevance, grammar, fluency, keyword_usage = scores
        
        # Calculate weighted scores
        weighted_relevance = relevance * self.weights.relevance
        weighted_grammar = grammar * self.weights.grammar
        weighted_fluency = fluency * self.weights.fluency
        weighted_keyword = keyword_usage * self.weights.keyword_usage
        
        # Total score
        total_score = (
            weighted_relevance +
            weighted_grammar +
            weighted_fluency +
            weighted_keyword
        )
        
        # Letter grade
        letter_grade = self._get_letter_grade(total_score)
        
        return ScoreBreakdown(
            relevance_score=round(relevance, 1),
            grammar_score=round(grammar, 1),
            fluency_score=round(fluency, 1),
            keyword_score=round(keyword_usage, 1),
            weighted_relevance=round(weighted_relevance, 2),
            weighted_grammar=round(weighted_grammar, 2),
            weighted_fluency=round(weighted_fluency, 2),
            weighted_keyword=round(weighted_keyword, 2),
            total_score=round(total_score, 1),
            letter_grade=letter_grade
        )
    
    def calculate_session_score(
        self,
        question_evaluations: List[Dict]
    ) -> SessionScore:
        """
        Calculate scores for an entire interview session.
        
        Args:
            question_evaluations: List of evaluation results per question
                Each dict should have:
                - question_id: str
                - relevance_score: float
                - grammar_score: float
                - fluency_score: float
                - keyword_score: float
                - time_taken: int (seconds)
                - response_length: int (words)
        
        Returns:
            SessionScore with complete scoring breakdown
        """
        if not question_evaluations:
            raise ValueError("No evaluations provided")
        
        question_scores = []
        score_trends = {
            'relevance': [],
            'grammar': [],
            'fluency': [],
            'keywords': [],
            'total': []
        }
        
        # Process each question
        for i, eval_data in enumerate(question_evaluations, 1):
            breakdown = self.calculate_final_score(
                relevance=eval_data.get('relevance_score', 0),
                grammar=eval_data.get('grammar_score', 0),
                fluency=eval_data.get('fluency_score', 0),
                keyword_usage=eval_data.get('keyword_score', 0)
            )
            
            question_score = QuestionScore(
                question_id=eval_data.get('question_id', str(i)),
                question_number=i,
                scores=breakdown,
                time_taken=eval_data.get('time_taken', 0),
                response_length=eval_data.get('response_length', 0)
            )
            question_scores.append(question_score)
            
            # Track trends
            score_trends['relevance'].append(breakdown.relevance_score)
            score_trends['grammar'].append(breakdown.grammar_score)
            score_trends['fluency'].append(breakdown.fluency_score)
            score_trends['keywords'].append(breakdown.keyword_score)
            score_trends['total'].append(breakdown.total_score)
        
        # Calculate averages
        n = len(question_scores)
        avg_relevance = sum(q.scores.relevance_score for q in question_scores) / n
        avg_grammar = sum(q.scores.grammar_score for q in question_scores) / n
        avg_fluency = sum(q.scores.fluency_score for q in question_scores) / n
        avg_keyword = sum(q.scores.keyword_score for q in question_scores) / n
        
        average_breakdown = self.calculate_final_score(
            relevance=avg_relevance,
            grammar=avg_grammar,
            fluency=avg_fluency,
            keyword_usage=avg_keyword
        )
        
        # Generate summary
        summary = self._generate_session_summary(
            average_breakdown,
            score_trends,
            len(question_scores)
        )
        
        return SessionScore(
            session_id="",  # To be set by caller
            question_scores=question_scores,
            average_scores=average_breakdown,
            total_score=average_breakdown.total_score,
            letter_grade=average_breakdown.letter_grade,
            performance_summary=summary,
            score_trends=score_trends
        )
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        for threshold, grade in self.GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_session_summary(
        self,
        avg_scores: ScoreBreakdown,
        trends: Dict[str, List[float]],
        num_questions: int
    ) -> str:
        """Generate performance summary for session."""
        
        grade = avg_scores.letter_grade
        score = avg_scores.total_score
        
        # Performance level
        if score >= 80:
            level = "Excellent performance"
        elif score >= 65:
            level = "Good performance"
        elif score >= 50:
            level = "Satisfactory performance"
        else:
            level = "Needs improvement"
        
        summary = f"{level} with overall grade {grade} ({score:.1f}/100). "
        summary += f"Completed {num_questions} questions. "
        
        # Identify strongest and weakest areas
        metrics = {
            'Relevance': avg_scores.relevance_score,
            'Grammar': avg_scores.grammar_score,
            'Fluency': avg_scores.fluency_score,
            'Topic Coverage': avg_scores.keyword_score
        }
        
        strongest = max(metrics.items(), key=lambda x: x[1])
        weakest = min(metrics.items(), key=lambda x: x[1])
        
        summary += f"Strongest area: {strongest[0]} ({strongest[1]:.1f}). "
        summary += f"Area to improve: {weakest[0]} ({weakest[1]:.1f}). "
        
        # Trend analysis
        total_trend = trends['total']
        if len(total_trend) >= 3:
            first_half = sum(total_trend[:len(total_trend)//2]) / (len(total_trend)//2)
            second_half = sum(total_trend[len(total_trend)//2:]) / (len(total_trend) - len(total_trend)//2)
            
            if second_half > first_half + 5:
                summary += "Performance improved throughout the session."
            elif first_half > second_half + 5:
                summary += "Performance declined towards the end - consider pacing."
            else:
                summary += "Performance was consistent throughout."
        
        return summary
    
    def calculate_percentile(
        self,
        score: float,
        historical_scores: List[float]
    ) -> int:
        """
        Calculate percentile rank based on historical scores.
        
        Args:
            score: Current score
            historical_scores: List of previous scores
        
        Returns:
            Percentile (0-100)
        """
        if not historical_scores:
            return 50  # Default to median
        
        below = sum(1 for s in historical_scores if s < score)
        percentile = (below / len(historical_scores)) * 100
        
        return int(round(percentile))
    
    def get_improvement_areas(
        self,
        breakdown: ScoreBreakdown
    ) -> List[Dict[str, str]]:
        """
        Get prioritized list of improvement areas.
        
        Args:
            breakdown: Score breakdown
        
        Returns:
            List of improvement recommendations
        """
        improvements = []
        
        metrics = [
            ('Relevance', breakdown.relevance_score, self.weights.relevance),
            ('Grammar', breakdown.grammar_score, self.weights.grammar),
            ('Fluency', breakdown.fluency_score, self.weights.fluency),
            ('Topic Coverage', breakdown.keyword_score, self.weights.keyword_usage)
        ]
        
        # Sort by impact (low score * high weight = high impact)
        metrics.sort(key=lambda x: (100 - x[1]) * x[2], reverse=True)
        
        for name, score, weight in metrics:
            if score < 70:  # Areas below 70 need improvement
                impact = "High" if (100 - score) * weight > 15 else "Medium"
                improvements.append({
                    'area': name,
                    'current_score': round(score, 1),
                    'target_score': 80,
                    'impact': impact,
                    'recommendation': self._get_recommendation(name, score)
                })
        
        return improvements
    
    def _get_recommendation(self, area: str, score: float) -> str:
        """Get specific recommendation for improvement area."""
        recommendations = {
            'Relevance': {
                'low': "Focus on directly addressing the question using the STAR method",
                'medium': "Improve focus on key aspects of the question"
            },
            'Grammar': {
                'low': "Practice with grammar checking tools and review common errors",
                'medium': "Pay attention to sentence structure and tense consistency"
            },
            'Fluency': {
                'low': "Practice speaking at a measured pace with clear structure",
                'medium': "Work on transitions between ideas and varying sentence length"
            },
            'Topic Coverage': {
                'low': "Research common topics for your target role and industry",
                'medium': "Include more specific technical terms and industry keywords"
            }
        }
        
        level = 'low' if score < 50 else 'medium'
        return recommendations.get(area, {}).get(level, "Continue practicing in this area")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_scoring_service(
    weights: Optional[ScoringWeights] = None
) -> ScoringService:
    """Factory function to get scoring service instance."""
    return ScoringService(weights=weights)
