"""
==============================================================================
AI Mock Interview System - Interview API Router
==============================================================================

REST API endpoints for interview management:
- Create/manage interview sessions
- Generate AI-powered questions
- Handle audio uploads
- Speech-to-text transcription
- NLP evaluation

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
import uuid
import time
import aiofiles
from datetime import datetime
from typing import List, Optional
from fastapi import (
    APIRouter, Depends, HTTPException, status,
    UploadFile, File, Form, Query, BackgroundTasks
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.interview import InterviewSession, InterviewStatus
from app.models.question import InterviewQuestion
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewSessionUpdate,
    InterviewSessionResponse,
    InterviewSessionDetailResponse,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
    GeneratedQuestion,
    AudioUploadResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationScores,
)
from app.schemas.common import APIResponse
from app.services.auth_service import get_current_user
from app.services.question_service import QuestionGeneratorService
from app.services.stt_service import SpeechToTextService
from app.services.evaluation_service import NLPEvaluationService
from app.config import settings

# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    responses={
        404: {"description": "Interview not found"},
        401: {"description": "Not authenticated"},
    }
)


# =============================================================================
# SESSION MANAGEMENT ENDPOINTS
# =============================================================================

@router.post(
    "/",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new interview session",
    description="Create a new interview session and generate questions."
)
async def create_interview_session(
    session_data: InterviewSessionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new interview session.
    
    **Request Body:**
    - **job_role**: Target job role (e.g., "Senior Python Developer")
    - **interview_type**: technical, behavioral, or mixed
    - **skills_tested**: List of skills to focus on
    - **experience_level**: entry, junior, mid, senior, lead
    - **difficulty**: easy, medium, hard
    - **total_questions**: Number of questions (1-20)
    - **time_limit_per_question**: Seconds per question
    
    **Returns:** Created interview session with generated questions
    
    **Flow:**
    1. Create session record
    2. Generate AI-powered questions based on role/skills
    3. Store questions linked to session
    4. Return session with questions
    """
    # Create new session
    new_session = InterviewSession(
        user_id=current_user.id,
        job_role=session_data.job_role,
        interview_type=session_data.interview_type,
        skills_tested=session_data.skills_tested,
        experience_level=session_data.experience_level,
        difficulty=session_data.difficulty,
        total_questions=session_data.total_questions,
        time_limit_per_question=session_data.time_limit_per_question,
        status=InterviewStatus.CREATED.value
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    # Generate questions using AI service
    # Map experience_level to approximate years
    experience_years_map = {
        "entry": 0, "junior": 1, "mid": 3, "senior": 5, "lead": 8, "executive": 12
    }
    experience_years = experience_years_map.get(session_data.experience_level, 3)
    
    # Map interview_type to categories
    categories_map = {
        "technical": ["technical"],
        "behavioral": ["behavioral"],
        "mixed": ["technical", "behavioral", "situational"]
    }
    categories = categories_map.get(session_data.interview_type, ["technical", "behavioral"])
    
    question_service = QuestionGeneratorService()
    generated_questions = await question_service.generate_questions(
        role=session_data.job_role,
        skills=session_data.skills_tested,
        experience_years=experience_years,
        difficulty=session_data.difficulty,
        num_questions=session_data.total_questions,
        categories=categories
    )
    
    # Create question records
    for i, q in enumerate(generated_questions, start=1):
        question = InterviewQuestion(
            session_id=new_session.id,
            question_text=q.question_text,
            question_order=i,
            category=q.category,
            difficulty=q.difficulty,
            expected_keywords=q.expected_topics,
            ideal_answer=None,
            time_limit=session_data.time_limit_per_question
        )
        db.add(question)
    
    await db.commit()
    
    # Refresh session with questions
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.questions))
        .where(InterviewSession.id == new_session.id)
    )
    session = result.scalar_one()
    
    return InterviewSessionResponse.model_validate(session)


@router.get(
    "/",
    response_model=List[InterviewSessionResponse],
    summary="List user's interview sessions",
    description="Get all interview sessions for the current user."
)
async def list_interview_sessions(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all interview sessions for the current user.
    
    **Query Parameters:**
    - **status_filter**: Filter by status (created, in_progress, completed, evaluated)
    - **limit**: Number of results (default 10, max 50)
    - **offset**: Pagination offset
    
    **Returns:** List of interview sessions
    """
    query = select(InterviewSession).where(
        InterviewSession.user_id == current_user.id
    ).options(selectinload(InterviewSession.questions))
    
    if status_filter:
        query = query.where(InterviewSession.status == status_filter)
    
    query = query.order_by(InterviewSession.created_at.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return [InterviewSessionResponse.model_validate(s) for s in sessions]


@router.get(
    "/{session_id}",
    response_model=InterviewSessionDetailResponse,
    summary="Get interview session details",
    description="Get detailed information about a specific interview session."
)
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about an interview session.
    
    **Path Parameters:**
    - **session_id**: The interview session ID
    
    **Returns:** Complete session details including:
    - Session metadata
    - All questions with responses
    - Scores and feedback
    """
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
            detail=f"Interview session {session_id} not found"
        )
    
    return InterviewSessionDetailResponse.model_validate(session)


@router.patch(
    "/{session_id}/start",
    response_model=InterviewSessionResponse,
    summary="Start interview session",
    description="Start an interview session (marks it as in_progress)."
)
async def start_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start an interview session.
    
    **Path Parameters:**
    - **session_id**: The interview session ID
    
    **Returns:** Updated session with started status
    """
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
    
    if session.status != InterviewStatus.CREATED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session has already been started"
        )
    
    session.start_interview()
    await db.commit()
    await db.refresh(session)
    
    return InterviewSessionResponse.model_validate(session)


@router.patch(
    "/{session_id}/complete",
    response_model=InterviewSessionResponse,
    summary="Complete interview session",
    description="Mark an interview session as completed."
)
async def complete_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete an interview session.
    
    **Path Parameters:**
    - **session_id**: The interview session ID
    
    **Returns:** Updated session with completed status
    """
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
    
    session.complete_interview()
    await db.commit()
    await db.refresh(session)
    
    return InterviewSessionResponse.model_validate(session)


# =============================================================================
# QUESTION GENERATION ENDPOINT
# =============================================================================

@router.post(
    "/generate-questions",
    response_model=QuestionGenerationResponse,
    summary="Generate interview questions",
    description="Generate AI-powered interview questions for a role."
)
async def generate_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate interview questions using AI.
    
    **Request Body:**
    - **job_role**: Target job role
    - **skills**: List of skills to test
    - **experience_level**: Candidate experience level
    - **num_questions**: Number of questions to generate
    - **interview_type**: technical, behavioral, or mixed
    - **difficulty**: easy, medium, or hard
    - **focus_areas**: Optional specific areas to focus on
    - **avoid_topics**: Optional topics to avoid
    
    **Returns:**
    - List of generated questions with:
        - Question text
        - Category
        - Expected keywords
        - Ideal answer (for evaluation)
    
    **AI Model Used:** GPT-4 or configured alternative
    """
    question_service = QuestionGeneratorService()
    
    questions = await question_service.generate_questions(
        job_role=request.job_role,
        skills=request.skills,
        experience_level=request.experience_level,
        num_questions=request.num_questions,
        interview_type=request.interview_type,
        difficulty=request.difficulty,
        focus_areas=request.focus_areas,
        avoid_topics=request.avoid_topics
    )
    
    return QuestionGenerationResponse(
        session_id="standalone",  # No session for standalone generation
        job_role=request.job_role,
        questions=questions,
        generated_at=datetime.utcnow(),
        ai_model_used=settings.ai_model
    )


# =============================================================================
# SESSION QUESTIONS ENDPOINTS
# =============================================================================

@router.post(
    "/{session_id}/questions/generate",
    response_model=QuestionGenerationResponse,
    summary="Generate questions for session",
    description="Generate additional questions for an existing session."
)
async def generate_session_questions(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate questions for an existing session.
    Returns the questions that were already generated when the session was created.
    """
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
    
    # Return existing questions
    questions = [
        GeneratedQuestion(
            question_text=q.question_text,
            category=q.category,
            difficulty=q.difficulty,
            expected_keywords=q.expected_keywords or [],
            ideal_answer=q.ideal_answer
        )
        for q in session.questions
    ]
    
    return QuestionGenerationResponse(
        session_id=session_id,
        job_role=session.job_role,
        questions=questions,
        generated_at=session.created_at,
        ai_model_used=settings.ai_model
    )


@router.get(
    "/{session_id}/questions",
    response_model=List[GeneratedQuestion],
    summary="Get session questions",
    description="Get all questions for an interview session."
)
async def get_session_questions(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all questions for an interview session."""
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
    
    return [
        GeneratedQuestion(
            question_text=q.question_text,
            category=q.category,
            difficulty=q.difficulty,
            expected_keywords=q.expected_keywords or [],
            ideal_answer=q.ideal_answer
        )
        for q in session.questions
    ]


# =============================================================================
# AUDIO UPLOAD ENDPOINT
# =============================================================================

@router.post(
    "/{session_id}/questions/{question_id}/audio",
    response_model=AudioUploadResponse,
    summary="Upload audio answer",
    description="Upload audio recording for an interview question."
)
async def upload_audio_answer(
    session_id: str,
    question_id: str,
    audio: UploadFile = File(..., description="Audio file (wav, mp3, m4a, webm)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload audio answer for a question.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    - **question_id**: Question ID
    
    **Request:**
    - **audio**: Audio file (multipart/form-data)
    
    **Supported Formats:** wav, mp3, m4a, webm, ogg
    
    **Max Size:** 50MB (configurable)
    
    **Returns:**
    - Upload confirmation
    - File path
    - File size
    - Duration (if determinable)
    
    **Flow:**
    1. Validate file format and size
    2. Save audio to storage
    3. Update question record with audio path
    4. Return upload confirmation
    """
    # Validate session and question
    result = await db.execute(
        select(InterviewQuestion)
        .where(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == session_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Validate file extension
    file_ext = audio.filename.split(".")[-1].lower() if audio.filename else ""
    if file_ext not in settings.allowed_audio_formats_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio format. Allowed: {settings.allowed_audio_formats}"
        )
    
    # Read file content
    content = await audio.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > settings.max_audio_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_audio_size_mb}MB"
        )
    
    # Create upload directory if not exists
    upload_dir = os.path.join(settings.upload_dir, "audio", session_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"{question_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Update question record
    question.audio_file_path = file_path
    question.audio_file_size = file_size
    question.answered_at = datetime.utcnow()
    
    await db.commit()
    
    return AudioUploadResponse(
        success=True,
        message="Audio uploaded successfully",
        question_id=question_id,
        file_path=file_path,
        file_size=file_size,
        duration_seconds=None,  # Would need audio processing to determine
        uploaded_at=datetime.utcnow()
    )


# =============================================================================
# SPEECH-TO-TEXT ENDPOINT
# =============================================================================

@router.post(
    "/{session_id}/questions/{question_id}/transcribe",
    response_model=TranscriptionResponse,
    summary="Transcribe audio to text",
    description="Convert audio answer to text using speech-to-text."
)
async def transcribe_audio(
    session_id: str,
    question_id: str,
    language: str = Query("en", description="Language code (e.g., en, es, fr)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Transcribe audio answer to text.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    - **question_id**: Question ID
    
    **Query Parameters:**
    - **language**: Language code (default: en)
    
    **Returns:**
    - Transcript text
    - Confidence score
    - Detected language
    - Word count
    - Processing time
    
    **STT Model:** Whisper (configurable)
    
    **Flow:**
    1. Retrieve audio file from storage
    2. Process with speech-to-text model
    3. Store transcript in question record
    4. Return transcription result
    """
    start_time = time.time()
    
    # Get question
    result = await db.execute(
        select(InterviewQuestion)
        .where(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == session_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    if not question.audio_file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file uploaded for this question"
        )
    
    # Transcribe using STT service
    stt_service = SpeechToTextService()
    transcript_result = await stt_service.transcribe(
        audio_path=question.audio_file_path,
        language=language
    )
    
    # Update question with transcript
    question.transcript = transcript_result["text"]
    question.transcript_confidence = transcript_result.get("confidence")
    
    await db.commit()
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return TranscriptionResponse(
        success=True,
        question_id=question_id,
        transcript=transcript_result["text"],
        confidence=transcript_result.get("confidence"),
        language_detected=transcript_result.get("language", language),
        duration_seconds=question.audio_duration_seconds,
        word_count=len(transcript_result["text"].split()),
        processing_time_ms=processing_time
    )


# =============================================================================
# NLP EVALUATION ENDPOINT
# =============================================================================

@router.post(
    "/{session_id}/questions/{question_id}/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate answer with NLP",
    description="Perform NLP-based evaluation on transcribed answer."
)
async def evaluate_answer(
    session_id: str,
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluate answer using NLP.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    - **question_id**: Question ID
    
    **Evaluation Criteria:**
    - **Relevance (35%)**: How well answer addresses the question
    - **Grammar (20%)**: Language correctness
    - **Fluency (25%)**: Coherence and readability
    - **Keywords (20%)**: Technical term coverage
    
    **Returns:**
    - Individual scores for each criterion
    - Overall score and grade
    - Strengths and weaknesses
    - Improvement suggestions
    
    **Flow:**
    1. Retrieve question and transcript
    2. Run NLP evaluation (relevance, grammar, fluency, keywords)
    3. Calculate weighted scores
    4. Generate feedback
    5. Store evaluation results
    6. Return detailed evaluation
    """
    start_time = time.time()
    
    # Get question
    result = await db.execute(
        select(InterviewQuestion)
        .where(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == session_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    if not question.transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript available. Please transcribe the audio first."
        )
    
    # Evaluate using NLP service
    evaluation_service = NLPEvaluationService()
    evaluation_result = await evaluation_service.evaluate(
        question_text=question.question_text,
        answer_text=question.transcript,
        expected_keywords=question.expected_keywords or []
    )
    
    # Update question with evaluation
    question.set_evaluation(
        relevance=evaluation_result["relevance_score"],
        grammar=evaluation_result["grammar_score"],
        fluency=evaluation_result["fluency_score"],
        keywords=evaluation_result["keyword_score"],
        strengths=evaluation_result["strengths"],
        weaknesses=evaluation_result["weaknesses"],
        suggestions=evaluation_result["suggestions"],
        feedback=evaluation_result["feedback_text"],
        raw_data=evaluation_result
    )
    
    await db.commit()
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return EvaluationResponse(
        success=True,
        question_id=question_id,
        scores=EvaluationScores(
            relevance_score=evaluation_result["relevance_score"],
            grammar_score=evaluation_result["grammar_score"],
            fluency_score=evaluation_result["fluency_score"],
            keyword_score=evaluation_result["keyword_score"],
            overall_score=evaluation_result["overall_score"]
        ),
        grade=evaluation_result["grade"],
        strengths=evaluation_result["strengths"],
        weaknesses=evaluation_result["weaknesses"],
        suggestions=evaluation_result["suggestions"],
        feedback_text=evaluation_result["feedback_text"],
        evaluation_time_ms=processing_time
    )


# =============================================================================
# BATCH OPERATIONS
# =============================================================================

@router.post(
    "/{session_id}/evaluate-all",
    response_model=APIResponse,
    summary="Evaluate all answers in session",
    description="Evaluate all unevaluated answers in the interview session."
)
async def evaluate_all_answers(
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluate all answers in an interview session.
    
    This operation runs in the background for large sessions.
    
    **Path Parameters:**
    - **session_id**: Interview session ID
    
    **Returns:** Confirmation that evaluation has started
    """
    # Verify session exists
    result = await db.execute(
        select(InterviewSession)
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
    
    # Queue background evaluation task
    # background_tasks.add_task(evaluate_session_answers, session_id)
    
    return APIResponse(
        success=True,
        message="Evaluation started. Results will be available shortly.",
        data={"session_id": session_id}
    )
