"""
==============================================================================
AI Mock Interview System - Scoring & Feedback API Router
==============================================================================

REST API endpoints for:
- Final interview scoring
- Feedback generation
- Interview history
- Dashboard statistics

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.interview import InterviewSession, InterviewStatus
from app.models.question import InterviewQuestion
from app.models.feedback import InterviewFeedback
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
    DashboardStatsResponse,
    PerformanceTrend,
    ChartDataResponse,
)
from app.schemas.common import APIResponse
from app.services.auth_service import get_current_user
from app.services.scoring_service import ScoringService
from app.services.feedback_service import FeedbackService

# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/feedback",
    tags=["Scoring & Feedback"],
    responses={
        404: {"description": "Resource not found"},
        401: {"description": "Not authenticated"},
    }
)


# =============================================================================
# SCORING ENDPOINTS
# =============================================================================

@router.post(
    "/score/{session_id}",
    response_model=ScoringResponse,
    summary="Calculate final interview scores",
    description="Calculate section-wise and total scores for an interview session."
)
async def calculate_scores(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate final scores for an interview session.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    
    **Scoring Logic:**
    1. Aggregate question scores by category
    2. Apply weights to each section:
       - Relevance: 35%
       - Grammar: 20%
       - Fluency: 25%
       - Keywords/Technical: 20%
    3. Calculate total weighted score
    4. Determine letter grade
    5. Calculate percentile (compared to other users)
    
    **Returns:**
    - Section-wise scores with weights
    - Total score and grade
    - Question statistics (best/worst scores)
    - Time analysis
    """
    # Get session with questions
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.questions))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    # Calculate scores using service
    scoring_service = ScoringService()
    scores = await scoring_service.calculate_session_scores(session)
    
    # Update session with scores
    session.overall_score = scores["total_score"]
    session.relevance_score = scores["relevance_score"]
    session.grammar_score = scores["grammar_score"]
    session.fluency_score = scores["fluency_score"]
    session.technical_score = scores["keyword_score"]
    session.grade = scores["grade"]
    session.status = InterviewStatus.EVALUATED.value
    
    # Update user statistics
    current_user.update_statistics(scores["total_score"])
    
    await db.commit()
    
    # Build section scores response
    section_scores = [
        SectionScore(
            section_name="Relevance",
            score=scores["relevance_score"],
            weight=0.35,
            weighted_score=scores["relevance_score"] * 0.35,
            feedback=_get_section_feedback("relevance", scores["relevance_score"])
        ),
        SectionScore(
            section_name="Grammar",
            score=scores["grammar_score"],
            weight=0.20,
            weighted_score=scores["grammar_score"] * 0.20,
            feedback=_get_section_feedback("grammar", scores["grammar_score"])
        ),
        SectionScore(
            section_name="Fluency",
            score=scores["fluency_score"],
            weight=0.25,
            weighted_score=scores["fluency_score"] * 0.25,
            feedback=_get_section_feedback("fluency", scores["fluency_score"])
        ),
        SectionScore(
            section_name="Technical/Keywords",
            score=scores["keyword_score"],
            weight=0.20,
            weighted_score=scores["keyword_score"] * 0.20,
            feedback=_get_section_feedback("keywords", scores["keyword_score"])
        ),
    ]
    
    return ScoringResponse(
        success=True,
        session_id=session_id,
        section_scores=section_scores,
        total_score=scores["total_score"],
        grade=scores["grade"],
        percentile=scores.get("percentile"),
        questions_answered=scores["questions_answered"],
        questions_skipped=scores["questions_skipped"],
        best_question_score=scores["best_question_score"],
        worst_question_score=scores["worst_question_score"],
        total_time_seconds=session.duration_seconds,
        average_time_per_question=scores["average_time_per_question"],
        calculated_at=datetime.utcnow()
    )


def _get_section_feedback(section: str, score: float) -> str:
    """Generate feedback text for a section score."""
    feedbacks = {
        "relevance": {
            80: "Excellent - your answers directly address the questions asked",
            60: "Good - mostly relevant with some tangential points",
            40: "Fair - answers could be more focused on the questions",
            0: "Needs improvement - answers don't adequately address the questions"
        },
        "grammar": {
            80: "Excellent - strong command of language and grammar",
            60: "Good - minor grammar issues that don't impact clarity",
            40: "Fair - several grammar errors affecting readability",
            0: "Needs improvement - significant grammar issues"
        },
        "fluency": {
            80: "Excellent - clear, well-structured responses",
            60: "Good - coherent with room for better flow",
            40: "Fair - some disjointed or unclear sections",
            0: "Needs improvement - responses lack clarity and structure"
        },
        "keywords": {
            80: "Excellent - strong use of technical terminology",
            60: "Good - adequate technical vocabulary",
            40: "Fair - missing some key technical terms",
            0: "Needs improvement - technical vocabulary is lacking"
        }
    }
    
    section_feedbacks = feedbacks.get(section, feedbacks["relevance"])
    for threshold, feedback in sorted(section_feedbacks.items(), reverse=True):
        if score >= threshold:
            return feedback
    return section_feedbacks[0]


# =============================================================================
# FEEDBACK GENERATION ENDPOINTS
# =============================================================================

@router.post(
    "/generate/{session_id}",
    response_model=FeedbackResponse,
    summary="Generate interview feedback",
    description="Generate comprehensive feedback for an interview session."
)
async def generate_feedback(
    session_id: str,
    include_resources: bool = Query(True, description="Include learning resources"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive feedback for an interview.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    
    **Query Parameters:**
    - **include_resources**: Include learning resources (default: true)
    
    **Feedback Includes:**
    - Executive summary
    - Detailed strengths with examples
    - Weaknesses with impact assessment
    - Prioritized improvement suggestions
    - Best and worst answer analysis
    - Job readiness assessment
    - Comparison with previous interviews
    - Recommended resources
    
    **Returns:** Comprehensive feedback report
    """
    # Get session with questions
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.questions))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    
    if not session.overall_score:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session has not been scored yet. Please score the session first."
        )
    
    # Generate feedback using service
    feedback_service = FeedbackService()
    feedback = await feedback_service.generate_feedback(
        session=session,
        user=current_user,
        include_resources=include_resources,
        db=db
    )
    
    # Store feedback in database
    feedback_record = InterviewFeedback(
        session_id=session_id,
        user_id=current_user.id,
        performance_rating=feedback["performance_rating"],
        executive_summary=feedback["executive_summary"],
        strengths=feedback["strengths"],
        weaknesses=feedback["weaknesses"],
        improvement_suggestions=feedback["suggestions"],
        job_readiness_score=feedback["job_readiness_score"],
        readiness_level=feedback["readiness_level"],
        improvement_percentage=feedback.get("improvement_percentage"),
        performance_trend=feedback.get("performance_trend"),
        recommended_resources=feedback.get("recommended_resources", []),
        practice_topics=feedback.get("practice_topics", [])
    )
    
    db.add(feedback_record)
    await db.commit()
    
    # Update session with aggregated feedback
    session.strengths = [s["area"] for s in feedback["strengths"]]
    session.weaknesses = [w["area"] for w in feedback["weaknesses"]]
    session.suggestions = [s["suggestion"] for s in feedback["suggestions"]]
    session.summary = feedback["executive_summary"]
    
    await db.commit()
    
    return FeedbackResponse(
        success=True,
        session_id=session_id,
        performance_rating=feedback["performance_rating"],
        executive_summary=feedback["executive_summary"],
        total_score=session.overall_score,
        grade=session.grade,
        strengths=[StrengthItem(**s) for s in feedback["strengths"]],
        weaknesses=[WeaknessItem(**w) for w in feedback["weaknesses"]],
        suggestions=[SuggestionItem(**s) for s in feedback["suggestions"]],
        best_answer=feedback.get("best_answer"),
        worst_answer=feedback.get("worst_answer"),
        job_readiness_score=feedback["job_readiness_score"],
        readiness_level=feedback["readiness_level"],
        estimated_practice_needed=feedback.get("estimated_practice_needed", 0),
        improvement_percentage=feedback.get("improvement_percentage"),
        performance_trend=feedback.get("performance_trend"),
        recommended_resources=feedback.get("recommended_resources", []),
        practice_topics=feedback.get("practice_topics", []),
        generated_at=datetime.utcnow()
    )


# =============================================================================
# INTERVIEW HISTORY ENDPOINTS
# =============================================================================

@router.get(
    "/history",
    response_model=InterviewHistoryResponse,
    summary="Get interview history",
    description="Get paginated interview history for the current user."
)
async def get_interview_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    interview_type: Optional[str] = Query(None, description="Filter by type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get interview history with pagination and filters.
    
    **Query Parameters:**
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 50)
    - **interview_type**: Filter by type (technical, behavioral, mixed)
    - **status_filter**: Filter by status
    - **date_from**: Start date filter
    - **date_to**: End date filter
    
    **Returns:**
    - Paginated list of interview sessions
    - Total count and pagination info
    """
    # Build query
    query = select(InterviewSession).where(
        InterviewSession.user_id == current_user.id
    )
    
    # Apply filters
    if interview_type:
        query = query.where(InterviewSession.interview_type == interview_type)
    if status_filter:
        query = query.where(InterviewSession.status == status_filter)
    if date_from:
        query = query.where(InterviewSession.created_at >= date_from)
    if date_to:
        query = query.where(InterviewSession.created_at <= date_to)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(InterviewSession.created_at.desc())
    query = query.offset(offset).limit(page_size)
    query = query.options(selectinload(InterviewSession.questions))
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    # Build response
    interviews = []
    for session in sessions:
        interviews.append(InterviewHistoryItem(
            session_id=session.id,
            job_role=session.job_role,
            interview_type=session.interview_type,
            total_score=session.overall_score,
            grade=session.grade,
            status=session.status,
            questions_count=len(session.questions),
            duration_seconds=session.duration_seconds,
            completed_at=session.completed_at,
            created_at=session.created_at
        ))
    
    total_pages = (total + page_size - 1) // page_size
    
    return InterviewHistoryResponse(
        user_id=current_user.id,
        total_interviews=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        interviews=interviews
    )


# =============================================================================
# DASHBOARD STATISTICS ENDPOINTS
# =============================================================================

@router.get(
    "/dashboard",
    response_model=DashboardStatsResponse,
    summary="Get dashboard statistics",
    description="Get comprehensive statistics for the user dashboard."
)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics.
    
    **Returns:**
    - Overview stats (total interviews, scores)
    - Recent performance trends (for charts)
    - Category breakdown
    - Skill analysis
    - Activity metrics
    - Progress toward goals
    """
    # Get all completed interviews
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status.in_([
                InterviewStatus.COMPLETED.value,
                InterviewStatus.EVALUATED.value
            ])
        )
        .order_by(InterviewSession.created_at.desc())
    )
    sessions = result.scalars().all()
    
    # Calculate statistics
    total_interviews = len(sessions)
    completed_interviews = sum(1 for s in sessions if s.overall_score is not None)
    
    scores = [s.overall_score for s in sessions if s.overall_score]
    average_score = sum(scores) / len(scores) if scores else 0
    best_score = max(scores) if scores else 0
    
    # Calculate total practice time
    total_seconds = sum(s.duration_seconds or 0 for s in sessions)
    total_hours = total_seconds / 3600
    
    # Recent scores for trend chart
    recent_sessions = sessions[:10]
    recent_scores = []
    for session in recent_sessions:
        if session.overall_score:
            recent_scores.append(PerformanceTrend(
                date=session.created_at.strftime("%Y-%m-%d"),
                score=session.overall_score,
                interview_type=session.interview_type,
                session_id=session.id
            ))
    
    # Calculate improvement trend
    if len(scores) >= 2:
        recent_avg = sum(scores[:5]) / min(len(scores), 5)
        older_avg = sum(scores[-5:]) / min(len(scores), 5)
        improvement = ((recent_avg - older_avg) / older_avg * 100) if older_avg else 0
        
        if improvement > 5:
            trend = "improving"
        elif improvement < -5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        improvement = 0
        trend = "stable"
    
    # Category scores
    category_scores = {}
    for session in sessions:
        if session.overall_score:
            itype = session.interview_type
            if itype not in category_scores:
                category_scores[itype] = []
            category_scores[itype].append(session.overall_score)
    
    category_averages = {
        k: sum(v) / len(v) for k, v in category_scores.items()
    }
    
    # Activity metrics
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    interviews_this_week = sum(
        1 for s in sessions if s.created_at >= week_ago
    )
    interviews_this_month = sum(
        1 for s in sessions if s.created_at >= month_ago
    )
    
    return DashboardStatsResponse(
        user_id=current_user.id,
        total_interviews=total_interviews,
        completed_interviews=completed_interviews,
        average_score=round(average_score, 2),
        best_score=round(best_score, 2),
        total_practice_hours=round(total_hours, 1),
        recent_scores=recent_scores,
        performance_trend=trend,
        improvement_percentage=round(improvement, 2),
        category_scores=category_averages,
        strongest_skills=current_user.skills[:3] if current_user.skills else [],
        weakest_skills=[],  # Would need more analysis
        interviews_this_week=interviews_this_week,
        interviews_this_month=interviews_this_month,
        current_streak=0,  # Would need streak calculation
        target_score=85.0,  # Could be user-configurable
        progress_to_target=(average_score / 85.0 * 100) if average_score else 0,
        generated_at=datetime.utcnow()
    )


@router.get(
    "/charts/performance",
    response_model=ChartDataResponse,
    summary="Get performance chart data",
    description="Get data for performance trend charts."
)
async def get_performance_chart_data(
    period: str = Query("month", description="Period: week, month, quarter, year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance chart data.
    
    **Query Parameters:**
    - **period**: Time period (week, month, quarter, year)
    
    **Returns:**
    - Chart configuration
    - Labels (dates)
    - Datasets (score values)
    """
    # Calculate date range
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Get sessions in range
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.created_at >= start_date,
            InterviewSession.overall_score.isnot(None)
        )
        .order_by(InterviewSession.created_at)
    )
    sessions = result.scalars().all()
    
    # Build chart data
    labels = []
    scores = []
    
    for session in sessions:
        labels.append(session.created_at.strftime("%b %d"))
        scores.append(session.overall_score)
    
    return ChartDataResponse(
        chart_type="line",
        title="Performance Over Time",
        labels=labels,
        datasets=[
            {
                "label": "Overall Score",
                "data": scores,
                "borderColor": "#4CAF50",
                "backgroundColor": "rgba(76, 175, 80, 0.1)",
                "tension": 0.4,
                "fill": True
            }
        ]
    )


@router.get(
    "/charts/score_trend",
    response_model=ChartDataResponse,
    summary="Get score trend chart data",
    description="Get data for score trend line chart."
)
async def get_score_trend_chart(
    period: str = Query("month", description="Period: week, month, quarter, year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get score trend data for charts."""
    now = datetime.utcnow()
    period_days = {"week": 7, "month": 30, "quarter": 90, "year": 365}
    start_date = now - timedelta(days=period_days.get(period, 30))
    
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.created_at >= start_date,
            InterviewSession.overall_score.isnot(None)
        )
        .order_by(InterviewSession.created_at)
    )
    sessions = result.scalars().all()
    
    labels = [s.created_at.strftime("%b %d") for s in sessions]
    scores = [s.overall_score for s in sessions]
    
    return ChartDataResponse(
        chart_type="line",
        title="Score Trend",
        labels=labels,
        datasets=[{
            "label": "Score",
            "data": scores,
            "borderColor": "#2196F3",
            "backgroundColor": "rgba(33, 150, 243, 0.1)",
            "tension": 0.4,
            "fill": True
        }]
    )


@router.get(
    "/charts/category_radar",
    response_model=ChartDataResponse,
    summary="Get category radar chart data",
    description="Get data for skills/category radar chart."
)
async def get_category_radar_chart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get category breakdown data for radar chart."""
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.overall_score.isnot(None)
        )
    )
    sessions = result.scalars().all()
    
    # Calculate average scores by category
    relevance_scores = [s.relevance_score for s in sessions if s.relevance_score]
    grammar_scores = [s.grammar_score for s in sessions if s.grammar_score]
    fluency_scores = [s.fluency_score for s in sessions if s.fluency_score]
    technical_scores = [s.technical_score for s in sessions if s.technical_score]
    
    labels = ["Relevance", "Grammar", "Fluency", "Technical"]
    data = [
        sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
        sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0,
        sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0,
        sum(technical_scores) / len(technical_scores) if technical_scores else 0,
    ]
    
    return ChartDataResponse(
        chart_type="radar",
        title="Skills Breakdown",
        labels=labels,
        datasets=[{
            "label": "Average Score",
            "data": data,
            "borderColor": "#9C27B0",
            "backgroundColor": "rgba(156, 39, 176, 0.2)",
        }]
    )


@router.get(
    "/charts/metrics_bar",
    response_model=ChartDataResponse,
    summary="Get metrics bar chart data",
    description="Get data for metrics comparison bar chart."
)
async def get_metrics_bar_chart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics breakdown data for bar chart."""
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.overall_score.isnot(None)
        )
        .order_by(InterviewSession.created_at.desc())
        .limit(10)
    )
    sessions = result.scalars().all()
    
    labels = [s.created_at.strftime("%b %d") for s in reversed(list(sessions))]
    
    return ChartDataResponse(
        chart_type="bar",
        title="Recent Performance Metrics",
        labels=labels,
        datasets=[
            {
                "label": "Relevance",
                "data": [s.relevance_score or 0 for s in reversed(list(sessions))],
                "backgroundColor": "#4CAF50",
            },
            {
                "label": "Grammar",
                "data": [s.grammar_score or 0 for s in reversed(list(sessions))],
                "backgroundColor": "#2196F3",
            },
            {
                "label": "Fluency",
                "data": [s.fluency_score or 0 for s in reversed(list(sessions))],
                "backgroundColor": "#FF9800",
            },
            {
                "label": "Technical",
                "data": [s.technical_score or 0 for s in reversed(list(sessions))],
                "backgroundColor": "#9C27B0",
            },
        ]
    )
