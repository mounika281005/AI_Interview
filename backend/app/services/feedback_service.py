"""
==============================================================================
AI Mock Interview System - Feedback Service
==============================================================================

Generates comprehensive feedback based on interview scores and evaluations.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FeedbackItem:
    """Individual feedback item."""
    category: str
    type: str  # 'strength', 'weakness', 'suggestion'
    message: str
    priority: int  # 1-5, lower is higher priority
    examples: List[str] = field(default_factory=list)


@dataclass
class ResourceRecommendation:
    """Learning resource recommendation."""
    title: str
    type: str  # 'article', 'video', 'course', 'practice'
    url: Optional[str]
    description: str
    skill_area: str


@dataclass
class InterviewFeedbackResult:
    """Complete feedback for an interview session."""
    session_id: str
    overall_rating: str
    overall_score: float
    summary: str
    strengths: List[FeedbackItem]
    weaknesses: List[FeedbackItem]
    suggestions: List[FeedbackItem]
    resources: List[ResourceRecommendation]
    readiness_score: int  # 0-100
    readiness_level: str
    next_steps: List[str]
    question_feedback: List[Dict[str, Any]]


# =============================================================================
# FEEDBACK TEMPLATES
# =============================================================================

STRENGTH_TEMPLATES = {
    'relevance': [
        "Excellent ability to stay focused on the question",
        "Strong connection between responses and question requirements",
        "Demonstrates clear understanding of what's being asked"
    ],
    'grammar': [
        "Professional and grammatically correct communication",
        "Clear and error-free language usage",
        "Strong command of English grammar"
    ],
    'fluency': [
        "Natural and flowing speech patterns",
        "Excellent vocabulary and sentence variety",
        "Clear and coherent response structure"
    ],
    'keywords': [
        "Comprehensive coverage of relevant topics",
        "Strong use of industry terminology",
        "Effective demonstration of technical knowledge"
    ]
}

WEAKNESS_TEMPLATES = {
    'relevance': [
        "Responses could be more directly focused on the question",
        "Consider structuring answers using the STAR method",
        "Some answers drifted from the main topic"
    ],
    'grammar': [
        "Some grammatical errors affected clarity",
        "Consider proofreading responses for common errors",
        "Sentence structure could be improved"
    ],
    'fluency': [
        "Response flow could be smoother",
        "Consider varying sentence length and structure",
        "Some hesitation affected response coherence"
    ],
    'keywords': [
        "Could include more technical terminology",
        "Expand coverage of expected topics",
        "Add more specific examples and details"
    ]
}

SUGGESTION_TEMPLATES = {
    'practice': [
        "Practice mock interviews regularly to build confidence",
        "Record yourself answering questions and review",
        "Practice with a timer to improve time management"
    ],
    'structure': [
        "Use the STAR method for behavioral questions",
        "Structure technical answers: context, approach, implementation, result",
        "Prepare 2-3 key examples that showcase different skills"
    ],
    'content': [
        "Research common questions for your target role",
        "Prepare specific metrics and outcomes from past experiences",
        "Stay updated on industry trends and technologies"
    ],
    'delivery': [
        "Speak at a measured pace - not too fast or slow",
        "Use pauses effectively for emphasis",
        "Practice eliminating filler words (um, like, you know)"
    ]
}


# =============================================================================
# FEEDBACK SERVICE
# =============================================================================

class FeedbackService:
    """
    Service for generating comprehensive interview feedback.
    
    Features:
    - Strength and weakness identification
    - Actionable improvement suggestions
    - Learning resource recommendations
    - Interview readiness assessment
    
    Usage:
        feedback_service = FeedbackService()
        feedback = feedback_service.generate_feedback(
            session_id="123",
            overall_score=72.5,
            metric_scores={
                'relevance': 75,
                'grammar': 68,
                'fluency': 78,
                'keywords': 70
            },
            question_results=[...]
        )
    """
    
    def __init__(self):
        """Initialize feedback service."""
        self.min_strength_score = 70
        self.min_weakness_score = 60
        logger.info("Feedback service initialized")
    
    def generate_feedback(
        self,
        session_id: str,
        overall_score: float,
        metric_scores: Dict[str, float],
        question_results: List[Dict[str, Any]],
        role: Optional[str] = None,
        experience_level: Optional[int] = None
    ) -> InterviewFeedbackResult:
        """
        Generate comprehensive feedback for an interview session.
        
        Args:
            session_id: Interview session ID
            overall_score: Overall interview score (0-100)
            metric_scores: Individual metric scores
            question_results: Results for each question
            role: Target job role
            experience_level: Years of experience
        
        Returns:
            InterviewFeedbackResult with complete feedback
        """
        # Generate rating
        overall_rating = self._get_rating(overall_score)
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(metric_scores)
        weaknesses = self._identify_weaknesses(metric_scores)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            metric_scores, weaknesses, role, experience_level
        )
        
        # Generate resource recommendations
        resources = self._recommend_resources(weaknesses, role)
        
        # Calculate readiness
        readiness_score, readiness_level = self._assess_readiness(
            overall_score, metric_scores, len(question_results)
        )
        
        # Generate summary
        summary = self._generate_summary(
            overall_score, overall_rating, strengths, weaknesses
        )
        
        # Generate next steps
        next_steps = self._generate_next_steps(
            readiness_level, weaknesses, role
        )
        
        # Generate per-question feedback
        question_feedback = self._generate_question_feedback(question_results)
        
        return InterviewFeedbackResult(
            session_id=session_id,
            overall_rating=overall_rating,
            overall_score=round(overall_score, 1),
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            resources=resources,
            readiness_score=readiness_score,
            readiness_level=readiness_level,
            next_steps=next_steps,
            question_feedback=question_feedback
        )
    
    def _get_rating(self, score: float) -> str:
        """Get overall rating based on score."""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Satisfactory"
        elif score >= 40:
            return "Needs Improvement"
        else:
            return "Below Expectations"
    
    def _identify_strengths(
        self,
        metric_scores: Dict[str, float]
    ) -> List[FeedbackItem]:
        """Identify strengths from metric scores."""
        strengths = []
        
        for metric, score in metric_scores.items():
            if score >= self.min_strength_score:
                templates = STRENGTH_TEMPLATES.get(metric, [])
                if templates:
                    # Select template based on score level
                    idx = min(2, int((score - 70) / 10))
                    message = templates[min(idx, len(templates) - 1)]
                    
                    strengths.append(FeedbackItem(
                        category=metric.capitalize(),
                        type='strength',
                        message=message,
                        priority=1 if score >= 85 else 2,
                        examples=[]
                    ))
        
        # Sort by priority
        strengths.sort(key=lambda x: x.priority)
        return strengths
    
    def _identify_weaknesses(
        self,
        metric_scores: Dict[str, float]
    ) -> List[FeedbackItem]:
        """Identify weaknesses from metric scores."""
        weaknesses = []
        
        for metric, score in metric_scores.items():
            if score < self.min_weakness_score:
                templates = WEAKNESS_TEMPLATES.get(metric, [])
                if templates:
                    # Select template based on score level
                    idx = 2 if score < 40 else (1 if score < 50 else 0)
                    message = templates[min(idx, len(templates) - 1)]
                    
                    weaknesses.append(FeedbackItem(
                        category=metric.capitalize(),
                        type='weakness',
                        message=message,
                        priority=1 if score < 40 else (2 if score < 50 else 3),
                        examples=[]
                    ))
        
        # Sort by priority (most critical first)
        weaknesses.sort(key=lambda x: x.priority)
        return weaknesses
    
    def _generate_suggestions(
        self,
        metric_scores: Dict[str, float],
        weaknesses: List[FeedbackItem],
        role: Optional[str],
        experience_level: Optional[int]
    ) -> List[FeedbackItem]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Add suggestions based on weaknesses
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            category = weakness.category.lower()
            
            # Map category to suggestion type
            suggestion_type = 'content' if category in ['relevance', 'keywords'] else 'delivery'
            templates = SUGGESTION_TEMPLATES.get(suggestion_type, [])
            
            if templates:
                suggestions.append(FeedbackItem(
                    category=weakness.category,
                    type='suggestion',
                    message=templates[0],
                    priority=weakness.priority,
                    examples=[]
                ))
        
        # Add general suggestions
        if not weaknesses:
            # Good performance - suggest maintenance
            suggestions.append(FeedbackItem(
                category='General',
                type='suggestion',
                message="Continue regular practice to maintain your performance level",
                priority=3,
                examples=[]
            ))
        
        # Add structure suggestions if needed
        avg_score = sum(metric_scores.values()) / len(metric_scores)
        if avg_score < 70:
            structure_templates = SUGGESTION_TEMPLATES.get('structure', [])
            suggestions.append(FeedbackItem(
                category='Structure',
                type='suggestion',
                message=structure_templates[0] if structure_templates else "Work on response structure",
                priority=2,
                examples=[]
            ))
        
        # Add practice suggestion
        practice_templates = SUGGESTION_TEMPLATES.get('practice', [])
        suggestions.append(FeedbackItem(
            category='Practice',
            type='suggestion',
            message=practice_templates[0] if practice_templates else "Practice regularly",
            priority=3,
            examples=[]
        ))
        
        return suggestions
    
    def _recommend_resources(
        self,
        weaknesses: List[FeedbackItem],
        role: Optional[str]
    ) -> List[ResourceRecommendation]:
        """Recommend learning resources based on weaknesses."""
        resources = []
        
        # Resource database (simplified)
        resource_db = {
            'relevance': ResourceRecommendation(
                title="STAR Method Interview Guide",
                type="article",
                url="https://www.indeed.com/career-advice/interviewing/star-interview-method",
                description="Learn how to structure behavioral interview responses",
                skill_area="Interview Structure"
            ),
            'grammar': ResourceRecommendation(
                title="Business English Communication",
                type="course",
                url="https://www.coursera.org/learn/business-english",
                description="Improve professional English communication skills",
                skill_area="Communication"
            ),
            'fluency': ResourceRecommendation(
                title="Public Speaking Fundamentals",
                type="video",
                url="https://www.youtube.com/results?search_query=interview+speaking+tips",
                description="Tips for clear and confident speech delivery",
                skill_area="Verbal Communication"
            ),
            'keywords': ResourceRecommendation(
                title="Technical Interview Preparation",
                type="practice",
                url="https://www.pramp.com/",
                description="Practice technical interviews with peers",
                skill_area="Technical Skills"
            )
        }
        
        # Add resources for each weakness
        for weakness in weaknesses:
            category = weakness.category.lower()
            if category in resource_db:
                resources.append(resource_db[category])
        
        # Always add a general resource
        resources.append(ResourceRecommendation(
            title="Mock Interview Practice",
            type="practice",
            url=None,
            description="Schedule regular mock interview sessions",
            skill_area="Overall Preparation"
        ))
        
        return resources
    
    def _assess_readiness(
        self,
        overall_score: float,
        metric_scores: Dict[str, float],
        num_questions: int
    ) -> tuple:
        """Assess interview readiness."""
        
        # Base readiness from overall score
        readiness = overall_score * 0.7
        
        # Bonus for consistency
        score_variance = max(metric_scores.values()) - min(metric_scores.values())
        if score_variance < 15:
            readiness += 10  # Consistent performance bonus
        
        # Bonus for completing more questions
        if num_questions >= 5:
            readiness += 5
        
        # Cap at 100
        readiness_score = int(min(100, max(0, readiness)))
        
        # Determine level
        if readiness_score >= 80:
            level = "Ready"
        elif readiness_score >= 60:
            level = "Almost Ready"
        elif readiness_score >= 40:
            level = "Needs Practice"
        else:
            level = "Not Ready"
        
        return readiness_score, level
    
    def _generate_summary(
        self,
        overall_score: float,
        rating: str,
        strengths: List[FeedbackItem],
        weaknesses: List[FeedbackItem]
    ) -> str:
        """Generate feedback summary."""
        
        summary = f"Your interview performance was rated as {rating} with an overall score of {overall_score:.1f}/100. "
        
        if strengths:
            strength_areas = [s.category for s in strengths[:2]]
            summary += f"Your strengths include {' and '.join(strength_areas).lower()}. "
        
        if weaknesses:
            weakness_areas = [w.category for w in weaknesses[:2]]
            summary += f"Areas for improvement include {' and '.join(weakness_areas).lower()}. "
        
        if overall_score >= 70:
            summary += "You're on the right track - keep practicing to maintain and improve your performance."
        else:
            summary += "With focused practice on the identified areas, you can significantly improve your interview performance."
        
        return summary
    
    def _generate_next_steps(
        self,
        readiness_level: str,
        weaknesses: List[FeedbackItem],
        role: Optional[str]
    ) -> List[str]:
        """Generate actionable next steps."""
        
        steps = []
        
        if readiness_level == "Ready":
            steps.extend([
                "You're ready for real interviews - start applying!",
                "Do a few more mock interviews to maintain confidence",
                "Research your target companies thoroughly"
            ])
        elif readiness_level == "Almost Ready":
            steps.extend([
                "Complete 2-3 more mock interview sessions",
                "Focus on your weakest area for improvement",
                "Start scheduling real interviews while continuing practice"
            ])
        else:
            steps.extend([
                "Schedule daily practice sessions (15-30 minutes)",
                "Work through the recommended resources",
                "Focus on one improvement area at a time"
            ])
        
        # Add weakness-specific steps
        for weakness in weaknesses[:2]:
            category = weakness.category.lower()
            if category == 'relevance':
                steps.append("Practice structuring responses with the STAR method")
            elif category == 'grammar':
                steps.append("Review common grammar rules and practice writing")
            elif category == 'fluency':
                steps.append("Practice speaking aloud and recording yourself")
            elif category == 'keywords':
                steps.append("Review job descriptions and industry terminology")
        
        return steps[:5]  # Return top 5 steps
    
    def _generate_question_feedback(
        self,
        question_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate feedback for each question."""
        
        feedback_list = []
        
        for i, result in enumerate(question_results, 1):
            score = result.get('overall_score', 0)
            
            feedback = {
                'question_number': i,
                'question_id': result.get('question_id', str(i)),
                'score': score,
                'rating': self._get_rating(score),
                'highlights': [],
                'improvements': []
            }
            
            # Add highlights for strong areas
            if result.get('relevance_score', 0) >= 70:
                feedback['highlights'].append("Good focus on the question")
            if result.get('fluency_score', 0) >= 70:
                feedback['highlights'].append("Clear and fluent response")
            
            # Add improvements for weak areas
            if result.get('relevance_score', 0) < 60:
                feedback['improvements'].append("Stay more focused on the question")
            if result.get('grammar_score', 0) < 60:
                feedback['improvements'].append("Review grammar and sentence structure")
            
            feedback_list.append(feedback)
        
        return feedback_list


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_feedback_service() -> FeedbackService:
    """Factory function to get feedback service instance."""
    return FeedbackService()
