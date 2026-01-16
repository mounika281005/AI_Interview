"""
==============================================================================
AI Mock Interview System - Statistics Service
==============================================================================

Calculates user statistics and analytics for the dashboard.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UserStats:
    """Comprehensive user statistics."""
    total_interviews: int
    total_questions_answered: int
    average_score: float
    best_score: float
    recent_score: float
    total_practice_time: int  # in minutes
    improvement_rate: float  # percentage
    current_streak: int
    longest_streak: int
    skills_breakdown: Dict[str, float]
    category_scores: Dict[str, float]


@dataclass 
class PerformanceTrend:
    """Performance trend data point."""
    date: str
    score: float
    num_questions: int
    session_id: Optional[str] = None


@dataclass
class ChartData:
    """Data for dashboard charts."""
    labels: List[str]
    datasets: List[Dict[str, Any]]


# =============================================================================
# STATISTICS SERVICE
# =============================================================================

class StatsService:
    """
    Service for calculating user statistics and analytics.
    
    Features:
    - Overall performance metrics
    - Score trends over time
    - Category-wise breakdown
    - Streak tracking
    - Chart data generation
    
    Usage:
        stats_service = StatsService(db_session)
        stats = await stats_service.get_user_stats(user_id)
        trends = await stats_service.get_performance_trends(user_id, days=30)
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        Initialize statistics service.
        
        Args:
            db: Database session (optional, can be passed to methods)
        """
        self.db = db
    
    async def get_user_stats(
        self,
        user_id: str,
        db: Optional[AsyncSession] = None
    ) -> UserStats:
        """
        Get comprehensive statistics for a user.
        
        Args:
            user_id: User ID
            db: Database session
        
        Returns:
            UserStats with all metrics
        """
        session = db or self.db
        if not session:
            raise ValueError("Database session required")
        
        from app.models.interview import InterviewSession, InterviewStatus
        from app.models.question import InterviewQuestion
        
        # Get all completed sessions
        sessions_result = await session.execute(
            select(InterviewSession)
            .where(
                and_(
                    InterviewSession.user_id == user_id,
                    InterviewSession.status == InterviewStatus.COMPLETED
                )
            )
            .order_by(desc(InterviewSession.created_at))
        )
        sessions = sessions_result.scalars().all()
        
        if not sessions:
            return self._empty_stats()
        
        # Calculate metrics
        total_interviews = len(sessions)
        scores = [s.overall_score or 0 for s in sessions if s.overall_score]
        
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        recent_score = scores[0] if scores else 0
        
        # Total questions
        questions_result = await session.execute(
            select(func.count(InterviewQuestion.id))
            .where(InterviewQuestion.session_id.in_([s.id for s in sessions]))
        )
        total_questions = questions_result.scalar() or 0
        
        # Calculate total practice time
        total_time = sum(s.total_duration or 0 for s in sessions) // 60
        
        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(scores)
        
        # Calculate streaks
        current_streak, longest_streak = self._calculate_streaks(sessions)
        
        # Skills breakdown
        skills_breakdown = await self._get_skills_breakdown(sessions, session)
        
        # Category scores
        category_scores = await self._get_category_scores(sessions, session)
        
        return UserStats(
            total_interviews=total_interviews,
            total_questions_answered=total_questions,
            average_score=round(average_score, 1),
            best_score=round(best_score, 1),
            recent_score=round(recent_score, 1),
            total_practice_time=total_time,
            improvement_rate=round(improvement_rate, 1),
            current_streak=current_streak,
            longest_streak=longest_streak,
            skills_breakdown=skills_breakdown,
            category_scores=category_scores
        )
    
    async def get_performance_trends(
        self,
        user_id: str,
        days: int = 30,
        db: Optional[AsyncSession] = None
    ) -> List[PerformanceTrend]:
        """
        Get performance trends over time.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            db: Database session
        
        Returns:
            List of PerformanceTrend data points
        """
        session = db or self.db
        if not session:
            raise ValueError("Database session required")
        
        from app.models.interview import InterviewSession, InterviewStatus
        from app.models.question import InterviewQuestion
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sessions in date range
        sessions_result = await session.execute(
            select(InterviewSession)
            .where(
                and_(
                    InterviewSession.user_id == user_id,
                    InterviewSession.status == InterviewStatus.COMPLETED,
                    InterviewSession.created_at >= since_date
                )
            )
            .order_by(InterviewSession.created_at)
        )
        sessions = sessions_result.scalars().all()
        
        trends = []
        for s in sessions:
            # Get question count for this session
            count_result = await session.execute(
                select(func.count(InterviewQuestion.id))
                .where(InterviewQuestion.session_id == s.id)
            )
            num_questions = count_result.scalar() or 0
            
            trends.append(PerformanceTrend(
                date=s.created_at.strftime("%Y-%m-%d"),
                score=round(s.overall_score or 0, 1),
                num_questions=num_questions,
                session_id=str(s.id)
            ))
        
        return trends
    
    async def get_chart_data(
        self,
        user_id: str,
        chart_type: str,
        db: Optional[AsyncSession] = None
    ) -> ChartData:
        """
        Get data formatted for charts.
        
        Args:
            user_id: User ID
            chart_type: Type of chart (score_trend, category_radar, etc.)
            db: Database session
        
        Returns:
            ChartData with labels and datasets
        """
        session = db or self.db
        
        if chart_type == "score_trend":
            return await self._get_score_trend_chart(user_id, session)
        elif chart_type == "category_radar":
            return await self._get_category_radar_chart(user_id, session)
        elif chart_type == "metrics_bar":
            return await self._get_metrics_bar_chart(user_id, session)
        elif chart_type == "weekly_activity":
            return await self._get_weekly_activity_chart(user_id, session)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
    
    async def _get_score_trend_chart(
        self,
        user_id: str,
        db: AsyncSession
    ) -> ChartData:
        """Generate score trend line chart data."""
        trends = await self.get_performance_trends(user_id, days=30, db=db)
        
        return ChartData(
            labels=[t.date for t in trends],
            datasets=[{
                'label': 'Overall Score',
                'data': [t.score for t in trends],
                'borderColor': '#4CAF50',
                'fill': False
            }]
        )
    
    async def _get_category_radar_chart(
        self,
        user_id: str,
        db: AsyncSession
    ) -> ChartData:
        """Generate category performance radar chart data."""
        stats = await self.get_user_stats(user_id, db)
        
        categories = list(stats.category_scores.keys())
        values = list(stats.category_scores.values())
        
        return ChartData(
            labels=categories,
            datasets=[{
                'label': 'Category Performance',
                'data': values,
                'backgroundColor': 'rgba(76, 175, 80, 0.2)',
                'borderColor': '#4CAF50',
                'pointBackgroundColor': '#4CAF50'
            }]
        )
    
    async def _get_metrics_bar_chart(
        self,
        user_id: str,
        db: AsyncSession
    ) -> ChartData:
        """Generate metrics comparison bar chart data."""
        stats = await self.get_user_stats(user_id, db)
        
        return ChartData(
            labels=['Relevance', 'Grammar', 'Fluency', 'Keywords'],
            datasets=[{
                'label': 'Average Score',
                'data': [
                    stats.skills_breakdown.get('relevance', 0),
                    stats.skills_breakdown.get('grammar', 0),
                    stats.skills_breakdown.get('fluency', 0),
                    stats.skills_breakdown.get('keywords', 0)
                ],
                'backgroundColor': [
                    '#4CAF50',
                    '#2196F3',
                    '#FFC107',
                    '#9C27B0'
                ]
            }]
        )
    
    async def _get_weekly_activity_chart(
        self,
        user_id: str,
        db: AsyncSession
    ) -> ChartData:
        """Generate weekly activity chart data."""
        from app.models.interview import InterviewSession
        
        # Get sessions from last 7 days
        since_date = datetime.utcnow() - timedelta(days=7)
        
        sessions_result = await db.execute(
            select(InterviewSession)
            .where(
                and_(
                    InterviewSession.user_id == user_id,
                    InterviewSession.created_at >= since_date
                )
            )
        )
        sessions = sessions_result.scalars().all()
        
        # Group by day of week
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        activity = {day: 0 for day in days}
        
        for s in sessions:
            day_name = s.created_at.strftime('%a')
            if day_name in activity:
                activity[day_name] += 1
        
        return ChartData(
            labels=days,
            datasets=[{
                'label': 'Sessions',
                'data': [activity[day] for day in days],
                'backgroundColor': '#4CAF50'
            }]
        )
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate improvement rate from scores."""
        if len(scores) < 2:
            return 0.0
        
        # Compare recent sessions to older ones
        half = len(scores) // 2
        recent_avg = sum(scores[:half]) / half if half > 0 else 0
        older_avg = sum(scores[half:]) / (len(scores) - half) if len(scores) > half else 0
        
        if older_avg > 0:
            improvement = ((recent_avg - older_avg) / older_avg) * 100
        else:
            improvement = 0
        
        return improvement
    
    def _calculate_streaks(self, sessions: List) -> tuple:
        """Calculate current and longest streaks."""
        if not sessions:
            return 0, 0
        
        # Group sessions by date
        dates = set()
        for s in sessions:
            dates.add(s.created_at.date())
        
        # Sort dates
        sorted_dates = sorted(dates, reverse=True)
        
        if not sorted_dates:
            return 0, 0
        
        # Current streak
        current_streak = 0
        today = datetime.utcnow().date()
        
        for i, date in enumerate(sorted_dates):
            expected = today - timedelta(days=i)
            if date == expected:
                current_streak += 1
            else:
                break
        
        # Longest streak
        longest_streak = 1
        current = 1
        
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i-1] - sorted_dates[i] == timedelta(days=1):
                current += 1
                longest_streak = max(longest_streak, current)
            else:
                current = 1
        
        return current_streak, longest_streak
    
    async def _get_skills_breakdown(
        self,
        sessions: List,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Get breakdown of scores by skill/metric."""
        from app.models.question import InterviewQuestion
        
        session_ids = [s.id for s in sessions]
        
        questions_result = await db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id.in_(session_ids))
        )
        questions = questions_result.scalars().all()
        
        if not questions:
            return {
                'relevance': 0,
                'grammar': 0,
                'fluency': 0,
                'keywords': 0
            }
        
        # Calculate averages
        relevance_scores = [q.relevance_score for q in questions if q.relevance_score]
        grammar_scores = [q.grammar_score for q in questions if q.grammar_score]
        fluency_scores = [q.fluency_score for q in questions if q.fluency_score]
        keyword_scores = [q.keyword_score for q in questions if q.keyword_score]
        
        return {
            'relevance': round(sum(relevance_scores) / len(relevance_scores), 1) if relevance_scores else 0,
            'grammar': round(sum(grammar_scores) / len(grammar_scores), 1) if grammar_scores else 0,
            'fluency': round(sum(fluency_scores) / len(fluency_scores), 1) if fluency_scores else 0,
            'keywords': round(sum(keyword_scores) / len(keyword_scores), 1) if keyword_scores else 0
        }
    
    async def _get_category_scores(
        self,
        sessions: List,
        db: AsyncSession
    ) -> Dict[str, float]:
        """Get scores breakdown by question category."""
        from app.models.question import InterviewQuestion
        
        session_ids = [s.id for s in sessions]
        
        questions_result = await db.execute(
            select(InterviewQuestion)
            .where(InterviewQuestion.session_id.in_(session_ids))
        )
        questions = questions_result.scalars().all()
        
        if not questions:
            return {}
        
        # Group by category
        category_scores = defaultdict(list)
        for q in questions:
            if q.category and q.overall_score:
                category_scores[q.category].append(q.overall_score)
        
        # Calculate averages
        return {
            cat: round(sum(scores) / len(scores), 1)
            for cat, scores in category_scores.items()
        }
    
    def _empty_stats(self) -> UserStats:
        """Return empty stats for new users."""
        return UserStats(
            total_interviews=0,
            total_questions_answered=0,
            average_score=0,
            best_score=0,
            recent_score=0,
            total_practice_time=0,
            improvement_rate=0,
            current_streak=0,
            longest_streak=0,
            skills_breakdown={
                'relevance': 0,
                'grammar': 0,
                'fluency': 0,
                'keywords': 0
            },
            category_scores={}
        )


# =============================================================================
# HELPER FUNCTION
# =============================================================================

async def calculate_user_stats(
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Calculate and return user statistics as a dictionary.
    
    This is a convenience function that can be called from routers.
    
    Args:
        user_id: User ID
        db: Database session
    
    Returns:
        Dictionary with all user statistics
    """
    service = StatsService(db)
    stats = await service.get_user_stats(user_id, db)
    
    return {
        'total_interviews': stats.total_interviews,
        'total_questions_answered': stats.total_questions_answered,
        'average_score': stats.average_score,
        'best_score': stats.best_score,
        'recent_score': stats.recent_score,
        'total_practice_time': stats.total_practice_time,
        'improvement_rate': stats.improvement_rate,
        'current_streak': stats.current_streak,
        'longest_streak': stats.longest_streak,
        'skills_breakdown': stats.skills_breakdown,
        'category_scores': stats.category_scores
    }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def get_stats_service(db: Optional[AsyncSession] = None) -> StatsService:
    """Factory function to get stats service instance."""
    return StatsService(db)
