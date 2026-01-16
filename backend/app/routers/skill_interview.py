"""
==============================================================================
AI Mock Interview System - Skill-Based Interview Router
==============================================================================

REST API endpoints for the streamlined skill-based interview flow:
1. Get available technologies
2. Generate questions for selected technology
3. Upload voice answers
4. Submit interview for evaluation
5. Get scores and feedback
6. Store results

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
import uuid
import time
import asyncio
import aiofiles
from datetime import datetime, timezone
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
from app.models.feedback import InterviewFeedback
from app.schemas.skill_interview import (
    Technology,
    TechnologyListResponse,
    SkillInterviewRequest,
    SkillInterviewResponse,
    SkillQuestion,
    QuestionScore,
    InterviewResult,
    InterviewHistoryItem,
    InterviewHistoryResponse,
)
from app.services.auth_service import get_current_user
from app.services.question_service import QuestionGeneratorService
from app.services.stt_service import SpeechToTextService
from app.services.evaluation_service import NLPEvaluationService
from app.config import settings

import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/skill-interview",
    tags=["Skill-Based Interview"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Not authenticated"},
    }
)

def debug_log(message: str, data: any = None):
    """Helper for consistent debug logging."""
    if data:
        logger.debug(f"{message}: {data}")
    else:
        logger.debug(message)

# =============================================================================
# TECHNOLOGY DATA
# =============================================================================

TECHNOLOGIES = [
    # Programming Languages
    {"id": "python", "name": "Python", "category": "Programming Languages", "icon": "🐍"},
    {"id": "javascript", "name": "JavaScript", "category": "Programming Languages", "icon": "💛"},
    {"id": "typescript", "name": "TypeScript", "category": "Programming Languages", "icon": "💙"},
    {"id": "java", "name": "Java", "category": "Programming Languages", "icon": "☕"},
    {"id": "csharp", "name": "C#", "category": "Programming Languages", "icon": "💜"},
    {"id": "cpp", "name": "C++", "category": "Programming Languages", "icon": "🔷"},
    {"id": "go", "name": "Go", "category": "Programming Languages", "icon": "🐹"},
    {"id": "rust", "name": "Rust", "category": "Programming Languages", "icon": "🦀"},
    {"id": "kotlin", "name": "Kotlin", "category": "Programming Languages", "icon": "🟣"},
    {"id": "swift", "name": "Swift", "category": "Programming Languages", "icon": "🍎"},
    
    # Frontend Frameworks
    {"id": "react", "name": "React", "category": "Frontend Frameworks", "icon": "⚛️"},
    {"id": "angular", "name": "Angular", "category": "Frontend Frameworks", "icon": "🅰️"},
    {"id": "vue", "name": "Vue.js", "category": "Frontend Frameworks", "icon": "💚"},
    {"id": "nextjs", "name": "Next.js", "category": "Frontend Frameworks", "icon": "▲"},
    {"id": "svelte", "name": "Svelte", "category": "Frontend Frameworks", "icon": "🔥"},
    
    # Backend Frameworks
    {"id": "nodejs", "name": "Node.js", "category": "Backend Frameworks", "icon": "💚"},
    {"id": "express", "name": "Express.js", "category": "Backend Frameworks", "icon": "🚂"},
    {"id": "fastapi", "name": "FastAPI", "category": "Backend Frameworks", "icon": "⚡"},
    {"id": "django", "name": "Django", "category": "Backend Frameworks", "icon": "🎸"},
    {"id": "flask", "name": "Flask", "category": "Backend Frameworks", "icon": "🍶"},
    {"id": "spring", "name": "Spring Boot", "category": "Backend Frameworks", "icon": "🍃"},
    {"id": "dotnet", "name": ".NET", "category": "Backend Frameworks", "icon": "🔷"},
    
    # Databases
    {"id": "sql", "name": "SQL", "category": "Databases", "icon": "🗃️"},
    {"id": "postgresql", "name": "PostgreSQL", "category": "Databases", "icon": "🐘"},
    {"id": "mongodb", "name": "MongoDB", "category": "Databases", "icon": "🍃"},
    {"id": "mysql", "name": "MySQL", "category": "Databases", "icon": "🐬"},
    {"id": "redis", "name": "Redis", "category": "Databases", "icon": "🔴"},
    
    # Cloud & DevOps
    {"id": "aws", "name": "AWS", "category": "Cloud & DevOps", "icon": "☁️"},
    {"id": "azure", "name": "Azure", "category": "Cloud & DevOps", "icon": "🔵"},
    {"id": "gcp", "name": "Google Cloud", "category": "Cloud & DevOps", "icon": "🌐"},
    {"id": "docker", "name": "Docker", "category": "Cloud & DevOps", "icon": "🐳"},
    {"id": "kubernetes", "name": "Kubernetes", "category": "Cloud & DevOps", "icon": "☸️"},
    {"id": "cicd", "name": "CI/CD", "category": "Cloud & DevOps", "icon": "🔄"},
    
    # Data & AI
    {"id": "machine-learning", "name": "Machine Learning", "category": "Data & AI", "icon": "🤖"},
    {"id": "deep-learning", "name": "Deep Learning", "category": "Data & AI", "icon": "🧠"},
    {"id": "data-science", "name": "Data Science", "category": "Data & AI", "icon": "📊"},
    {"id": "nlp", "name": "NLP", "category": "Data & AI", "icon": "💬"},
    
    # Others
    {"id": "system-design", "name": "System Design", "category": "Architecture", "icon": "🏗️"},
    {"id": "dsa", "name": "Data Structures & Algorithms", "category": "Fundamentals", "icon": "📐"},
    {"id": "git", "name": "Git", "category": "Tools", "icon": "📦"},
    {"id": "rest-api", "name": "REST API", "category": "Architecture", "icon": "🔌"},
    {"id": "graphql", "name": "GraphQL", "category": "Architecture", "icon": "◼️"},
]

IDEAL_ANSWERS = {
    "python": {
        "What are Python's key features?": "Python's key features include: 1) Easy to read and write syntax with significant whitespace, 2) Dynamic typing - no need to declare variable types, 3) Interpreted language for rapid development, 4) Extensive standard library, 5) Support for multiple programming paradigms (OOP, functional, procedural), 6) Strong community and ecosystem with PyPI, 7) Memory management with garbage collection, 8) Cross-platform compatibility.",
        
        "Explain the difference between lists and tuples in Python.": "Lists and tuples are both sequence types in Python, but differ in key ways: 1) Mutability - Lists are mutable (can be modified), while tuples are immutable (cannot be changed after creation), 2) Syntax - Lists use square brackets [], tuples use parentheses (), 3) Performance - Tuples are slightly faster and use less memory, 4) Use cases - Lists for collections that need modification, tuples for fixed data like coordinates or function returns, 5) Methods - Lists have more methods (append, extend, insert, remove), tuples have fewer.",
        
        "What are decorators in Python and how do they work?": "Decorators are functions that modify the behavior of other functions without changing their source code. They work by: 1) Taking a function as input, 2) Wrapping it with additional functionality, 3) Returning the modified function. Common uses include logging, authentication, timing, and caching. Example: @decorator syntax is syntactic sugar for func = decorator(func). They use closures to preserve the wrapped function and can accept arguments using nested functions.",
        
        "Explain the GIL (Global Interpreter Lock) in Python.": "The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time. Key points: 1) It simplifies memory management and prevents race conditions in CPython, 2) It limits true parallelism in CPU-bound multithreaded programs, 3) I/O-bound programs can still benefit from threading as GIL is released during I/O, 4) For CPU-bound tasks, use multiprocessing module instead, 5) Some Python implementations like Jython and IronPython don't have GIL.",
        
        "What are generators and how are they different from regular functions?": "Generators are functions that yield values one at a time using the yield keyword instead of return. Differences: 1) Memory efficiency - generators produce values lazily, one at a time, 2) State preservation - generators maintain state between calls, 3) Iteration protocol - generators are iterators automatically, 4) Use yield instead of return - function execution pauses and resumes, 5) Useful for large datasets or infinite sequences. Generator expressions are similar but use parentheses syntax.",
    },
    "javascript": {
        "What is the event loop in JavaScript?": "The event loop is JavaScript's mechanism for handling asynchronous operations in a single-threaded environment. It works by: 1) Executing synchronous code in the call stack, 2) Moving async callbacks to the callback queue when complete, 3) Continuously checking if call stack is empty, 4) Moving callbacks from queue to call stack when empty. Components include: call stack, web APIs, callback queue, microtask queue (for Promises). Microtasks have priority over macrotasks.",
        
        "Explain closures in JavaScript.": "A closure is a function that has access to variables from its outer (enclosing) scope even after the outer function has returned. Key aspects: 1) Functions remember their lexical environment, 2) Inner functions can access outer function's variables, 3) Enables data privacy and encapsulation, 4) Used in module patterns, callbacks, and currying. Common use cases include creating private variables, function factories, and maintaining state in async operations.",
        
        "What is the difference between let, const, and var?": "These are variable declarations with different scoping and mutability: 1) var - function-scoped, hoisted with undefined, can be redeclared, 2) let - block-scoped, hoisted but not initialized (temporal dead zone), cannot be redeclared, 3) const - block-scoped, must be initialized, cannot be reassigned (but objects can be mutated). Best practices: prefer const by default, use let when reassignment needed, avoid var in modern code.",
        
        "Explain Promises and async/await in JavaScript.": "Promises represent eventual completion or failure of async operations. They have three states: pending, fulfilled, rejected. Methods include then(), catch(), finally(). async/await is syntactic sugar for Promises: async functions return Promises, await pauses execution until Promise resolves. Benefits: cleaner code, better error handling with try/catch, easier debugging. Use Promise.all() for parallel operations, Promise.race() for first completion.",
        
        "What is prototypal inheritance in JavaScript?": "JavaScript uses prototypal inheritance where objects inherit directly from other objects via the prototype chain. Key concepts: 1) Every object has a [[Prototype]] internal property, 2) Property lookup traverses the prototype chain, 3) Object.create() creates objects with specified prototype, 4) Constructor functions use .prototype property, 5) ES6 classes are syntactic sugar over prototypes. Unlike classical inheritance, objects can inherit from multiple sources and prototypes can be modified at runtime.",
    },
    "react": {
        "What is the Virtual DOM and how does React use it?": "The Virtual DOM is a lightweight JavaScript representation of the actual DOM. React uses it for efficient updates: 1) Creates virtual DOM tree on state change, 2) Compares (diffs) new and old virtual trees, 3) Calculates minimal changes needed, 4) Batches and applies updates to real DOM. Benefits include better performance, declarative programming, and abstraction from browser DOM. React Fiber (React 16+) improved this with incremental rendering.",
        
        "Explain the difference between state and props.": "State and props are both JavaScript objects that influence component rendering: State - 1) Managed within component, 2) Mutable via setState/useState, 3) Private to component, 4) Triggers re-render when changed. Props - 1) Passed from parent, 2) Immutable (read-only), 3) Component's configuration, 4) Used for parent-child communication. State is for data that changes over time, props are for component customization.",
        
        "What are React Hooks and why were they introduced?": "Hooks are functions that let you use state and lifecycle features in functional components. Introduced in React 16.8. Key hooks: useState for state, useEffect for side effects, useContext for context, useRef for refs, useMemo/useCallback for optimization. Benefits: 1) Share stateful logic between components, 2) Avoid class complexity, 3) Better code organization, 4) Easier testing. Rules: only call at top level, only call from React functions.",
        
        "How does useEffect work and when should you use it?": "useEffect handles side effects in functional components. It runs after render and replaces componentDidMount, componentDidUpdate, componentWillUnmount. Usage: 1) No dependency array - runs after every render, 2) Empty array [] - runs once on mount, 3) With dependencies - runs when dependencies change. Return a cleanup function for subscriptions/timers. Common uses: data fetching, subscriptions, DOM manipulation, timers.",
        
        "Explain React's reconciliation algorithm.": "Reconciliation is how React updates the DOM efficiently. Key principles: 1) Different element types produce different trees, 2) Keys help identify moved elements, 3) Component type comparison determines subtree updates. Process: compare root elements, if different type replace entire subtree, if same type update attributes and recurse on children. Keys should be stable, predictable, and unique among siblings. Avoid array indices as keys for dynamic lists.",
    },
}


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get(
    "/technologies",
    response_model=TechnologyListResponse,
    summary="Get available technologies",
    description="Get list of all available technologies/skills for interview."
)
async def get_technologies():
    """
    Get all available technologies for interview.
    
    Returns list of technologies grouped by category.
    """
    technologies = [Technology(**tech) for tech in TECHNOLOGIES]
    categories = list(set(tech["category"] for tech in TECHNOLOGIES))
    
    return TechnologyListResponse(
        technologies=technologies,
        categories=sorted(categories)
    )


@router.post(
    "/start",
    response_model=SkillInterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start skill-based interview",
    description="Generate 5 interview questions for selected technology."
)
async def start_skill_interview(
    request: SkillInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new skill-based interview.
    
    1. Validates technology selection
    2. Creates interview session
    3. Generates 5 questions for the technology
    4. Returns session with questions
    """
    debug_log("=== START SKILL INTERVIEW ===")
    debug_log("Request received", {
        "technology": request.technology,
        "num_questions": request.num_questions,
        "difficulty": request.difficulty,
        "user_id": current_user.id
    })
    
    # Validate technology
    tech_ids = [t["id"] for t in TECHNOLOGIES]
    tech_names = [t["name"].lower() for t in TECHNOLOGIES]
    
    if request.technology.lower() not in tech_names and request.technology.lower() not in tech_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid technology. Available: {', '.join(t['name'] for t in TECHNOLOGIES[:10])}..."
        )
    
    # Find technology name
    tech_name = request.technology
    for tech in TECHNOLOGIES:
        if tech["id"] == request.technology.lower() or tech["name"].lower() == request.technology.lower():
            tech_name = tech["name"]
            break
    
    # Create session
    new_session = InterviewSession(
        user_id=current_user.id,
        job_role=f"{tech_name} Developer",
        interview_type="technical",
        skills_tested=[tech_name],
        experience_level="mid",
        difficulty=request.difficulty,
        total_questions=request.num_questions,
        time_limit_per_question=120,
        status=InterviewStatus.CREATED.value
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    debug_log("Session created", {"session_id": new_session.id, "status": new_session.status})
    
    # Generate questions using AI service
    debug_log("Generating questions...")
    question_service = QuestionGeneratorService()
    
    try:
        generated_questions = await question_service.generate_questions(
            role=f"{tech_name} Developer",
            skills=[tech_name],
            experience_years=3,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            categories=["technical"]
        )
    except Exception as e:
        logger.warning(f"AI question generation failed: {e}, using fallback")
        debug_log("AI generation failed, using fallback", str(e))
        # Use fallback questions
        generated_questions = _get_fallback_questions(tech_name, request.num_questions, request.difficulty)
    
    debug_log("Questions generated", {"count": len(generated_questions)})
    
    # Create question records
    skill_questions = []
    for i, q in enumerate(generated_questions, start=1):
        # Get ideal answer if available
        tech_key = tech_name.lower()
        ideal_answer = None
        
        # Handle both Pydantic model and dict formats
        q_text = getattr(q, 'question_text', '') if hasattr(q, 'question_text') else (q.get('question_text', '') if isinstance(q, dict) else '')
        q_keywords = getattr(q, 'expected_topics', []) if hasattr(q, 'expected_topics') else (q.get('expected_keywords', []) if isinstance(q, dict) else [])
        q_ideal = getattr(q, 'ideal_answer', None) if hasattr(q, 'ideal_answer') else (q.get('ideal_answer') if isinstance(q, dict) else None)
        
        if tech_key in IDEAL_ANSWERS:
            for stored_q, stored_a in IDEAL_ANSWERS.get(tech_key, {}).items():
                if stored_q.lower() in q_text.lower() or q_text.lower() in stored_q.lower():
                    ideal_answer = stored_a
                    break
        
        question = InterviewQuestion(
            session_id=new_session.id,
            question_text=q_text,
            question_order=i,
            category=tech_name,
            difficulty=request.difficulty,
            expected_keywords=q_keywords,
            ideal_answer=ideal_answer or q_ideal,
            time_limit=120
        )
        db.add(question)
        await db.flush()  # Flush to get the question ID
        
        skill_questions.append(SkillQuestion(
            id=question.id,
            question_number=i,
            question_text=question.question_text,
            technology=tech_name,
            difficulty=request.difficulty,
            expected_keywords=question.expected_keywords or [],
            ideal_answer=question.ideal_answer,
            time_limit_seconds=120
        ))
    
    await db.commit()
    
    # Update session status
    new_session.status = InterviewStatus.IN_PROGRESS.value
    new_session.started_at = datetime.now(timezone.utc)
    await db.commit()
    
    return SkillInterviewResponse(
        session_id=new_session.id,
        technology=tech_name,
        difficulty=request.difficulty,
        total_questions=request.num_questions,
        questions=skill_questions,
        created_at=new_session.created_at
    )


@router.post(
    "/{session_id}/upload-audio/{question_id}",
    summary="Upload voice answer for a question",
    description="Upload recorded audio answer for a specific question."
)
async def upload_audio_answer(
    session_id: str,
    question_id: str,
    audio: UploadFile = File(...),
    duration_seconds: float = Form(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload audio recording for a question.
    
    Accepts audio file (wav, mp3, webm, m4a) and stores it for processing.
    """
    debug_log("=== UPLOAD AUDIO ===")
    debug_log("Input params", {
        "session_id": session_id,
        "question_id": question_id,
        "filename": audio.filename if audio else None,
        "duration_seconds": duration_seconds,
        "user_id": current_user.id
    })
    
    # Validate session
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        debug_log("ERROR: Session not found", session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    debug_log("Session found", {"status": session.status})
    
    # Validate question
    result = await db.execute(
        select(InterviewQuestion).where(
            InterviewQuestion.id == question_id,
            InterviewQuestion.session_id == session_id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        debug_log("ERROR: Question not found", question_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    debug_log("Question found", {"question_order": question.question_order})
    
    # Validate file
    if not audio.filename:
        debug_log("ERROR: No filename")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_ext = audio.filename.split('.')[-1].lower()
    debug_log("File extension", file_ext)
    
    if file_ext not in ['wav', 'mp3', 'webm', 'm4a', 'ogg']:
        debug_log("ERROR: Invalid format", file_ext)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio format. Supported: wav, mp3, webm, m4a, ogg"
        )
    
    # Create upload directory
    upload_dir = os.path.join(settings.upload_dir, "audio", session_id)
    os.makedirs(upload_dir, exist_ok=True)
    debug_log("Upload directory", upload_dir)
    
    # Save file
    filename = f"{question_id}.{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        content = await audio.read()
        await f.write(content)
    
    file_size = len(content)
    debug_log("File saved", {"path": file_path, "size": file_size})
    
    # Update question record
    question.audio_file_path = file_path
    question.audio_file_size = file_size
    question.audio_duration_seconds = duration_seconds
    question.answered_at = datetime.now(timezone.utc)
    
    await db.commit()
    debug_log("Audio upload COMPLETE")
    
    return {
        "success": True,
        "message": "Audio uploaded successfully",
        "question_id": question_id,
        "file_path": file_path,
        "file_size": file_size,
        "duration_seconds": duration_seconds
    }


@router.post(
    "/{session_id}/submit",
    response_model=InterviewResult,
    summary="Submit interview for evaluation",
    description="Process all answers: transcribe, evaluate, score, and generate feedback."
)
async def submit_interview(
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit the complete interview for evaluation.
    
    1. Transcribe all audio answers (Speech-to-Text)
    2. Evaluate each answer using NLP
    3. Score on grammar, fluency, structure, similarity
    4. Generate feedback and ideal answers
    5. Store results in database
    6. Return complete results
    """
    debug_log("=== SUBMIT INTERVIEW ===")
    debug_log("Session ID", session_id)
    debug_log("User ID", current_user.id)
    
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
        debug_log("ERROR: Session not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    questions = sorted(session.questions, key=lambda q: q.question_order)
    debug_log("Questions found", len(questions))
    
    # Check if answers are provided
    answered_questions = [q for q in questions if q.audio_file_path]
    debug_log("Answered questions", len(answered_questions))
    
    if not answered_questions:
        debug_log("ERROR: No answers recorded")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers recorded. Please record answers before submitting."
        )
    
    # Initialize services
    debug_log("Initializing STT and Evaluation services...")
    try:
        stt_service = SpeechToTextService()
        debug_log("STT service initialized")
    except Exception as e:
        debug_log("STT service init FAILED, using fallback", str(e))
        stt_service = None
    
    try:
        evaluation_service = NLPEvaluationService()
        debug_log("Evaluation service initialized")
    except Exception as e:
        debug_log("Evaluation service init FAILED, using fallback", str(e))
        evaluation_service = None
    
    question_scores = []
    total_grammar = 0
    total_fluency = 0
    total_structure = 0
    total_similarity = 0
    
    technology = session.skills_tested[0] if session.skills_tested else "General"
    debug_log("Technology", technology)
    
    for i, question in enumerate(questions):
        debug_log(f"Processing question {i+1}/{len(questions)}", question.id)
        transcript = ""
        
        # Step 1: Transcribe audio
        if question.audio_file_path and os.path.exists(question.audio_file_path):
            debug_log("Transcribing audio", question.audio_file_path)
            if stt_service:
                try:
                    transcription_result = await stt_service.transcribe(question.audio_file_path)
                    transcript = transcription_result.text
                    question.transcript = transcript
                    question.transcript_confidence = transcription_result.confidence
                    debug_log("Transcription SUCCESS", {"length": len(transcript)})
                except Exception as e:
                    debug_log("Transcription FAILED", str(e))
                    logger.error(f"Transcription failed for question {question.id}: {e}")
                    transcript = "[Transcription service unavailable - audio was recorded]"
                    question.transcript = transcript
            else:
                transcript = "[Transcription service unavailable - audio was recorded]"
                question.transcript = transcript
        else:
            debug_log("No audio file", question.audio_file_path)
            transcript = "[No audio recorded]"
            question.transcript = transcript
        
        # Step 2: Evaluate answer
        if transcript and not transcript.startswith("[") and evaluation_service:
            debug_log("Evaluating answer...")
            try:
                eval_result = await evaluation_service.evaluate(
                    question=question.question_text,
                    response=transcript,
                    expected_keywords=question.expected_keywords,
                    context=technology
                )
                
                # Convert 0-100 scores to 0-5 scale
                grammar_score = min(5.0, eval_result.grammar.score / 20)
                fluency_score = min(5.0, eval_result.fluency.score / 20)
                structure_score = min(5.0, eval_result.relevance.score / 20)  # Using relevance as structure
                similarity_score = min(5.0, eval_result.keyword_usage.score / 20)
                
                overall_score = (grammar_score + fluency_score + structure_score + similarity_score) / 4
                debug_log("Evaluation SUCCESS", {"overall": overall_score})
                
                strengths = eval_result.strengths
                improvements = eval_result.improvements
                
            except Exception as e:
                debug_log("Evaluation FAILED", str(e))
                logger.error(f"Evaluation failed for question {question.id}: {e}")
                # Fallback scores for audio that was recorded but couldn't be evaluated
                grammar_score = 3.0
                fluency_score = 3.0
                structure_score = 3.0
                similarity_score = 3.0
                overall_score = 3.0
                strengths = ["Answer was provided", "Audio recorded successfully"]
                improvements = ["Evaluation service unavailable for detailed analysis"]
        elif transcript and transcript.startswith("["):
            # No valid transcription
            grammar_score = 2.5
            fluency_score = 2.5
            structure_score = 2.5
            similarity_score = 2.5
            overall_score = 2.5
            strengths = ["Answer was attempted"]
            improvements = ["Transcription could not be completed - check audio quality"]
        else:
            # No valid answer
            grammar_score = 0
            fluency_score = 0
            structure_score = 0
            similarity_score = 0
            overall_score = 0
            strengths = []
            improvements = ["No valid answer provided"]
        
        # Update question with scores
        question.grammar_score = grammar_score * 20  # Store as 0-100
        question.fluency_score = fluency_score * 20
        question.relevance_score = structure_score * 20
        question.keyword_score = similarity_score * 20
        question.overall_score = overall_score * 20
        question.strengths = strengths
        question.weaknesses = improvements
        question.is_evaluated = True
        question.evaluated_at = datetime.now(timezone.utc)
        
        # Get ideal answer
        ideal_answer = question.ideal_answer
        if not ideal_answer:
            ideal_answer = _generate_ideal_answer(technology, question.question_text)
            question.ideal_answer = ideal_answer
        
        # Add to totals
        total_grammar += grammar_score
        total_fluency += fluency_score
        total_structure += structure_score
        total_similarity += similarity_score
        
        # Create question score response
        question_scores.append(QuestionScore(
            question_id=question.id,
            question_number=question.question_order,
            question_text=question.question_text,
            transcript=transcript,
            grammar_score=round(grammar_score, 1),
            fluency_score=round(fluency_score, 1),
            structure_score=round(structure_score, 1),
            similarity_score=round(similarity_score, 1),
            overall_score=round(overall_score, 1),
            strengths=strengths[:3],
            improvements=improvements[:3],
            ideal_answer=ideal_answer
        ))
    
    # Calculate final scores
    num_questions = len(questions)
    max_possible = num_questions * 5.0
    total_score = sum(qs.overall_score for qs in question_scores)
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    # Determine grade
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B+"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 50:
        grade = "C"
    elif percentage >= 40:
        grade = "D"
    else:
        grade = "F"
    
    # Generate performance summary
    if percentage >= 80:
        performance_summary = f"Excellent performance! You demonstrated strong knowledge of {technology} with clear and well-structured answers."
    elif percentage >= 60:
        performance_summary = f"Good performance. You showed solid understanding of {technology} fundamentals with room for improvement in some areas."
    elif percentage >= 40:
        performance_summary = f"Satisfactory performance. You have basic understanding of {technology} but need to work on technical depth and clarity."
    else:
        performance_summary = f"Needs improvement. Consider reviewing {technology} fundamentals and practice explaining concepts more clearly."
    
    # Aggregate strengths and improvements
    all_strengths = []
    all_improvements = []
    for qs in question_scores:
        all_strengths.extend(qs.strengths)
        all_improvements.extend(qs.improvements)
    
    # Get unique items
    overall_strengths = list(set(all_strengths))[:5]
    overall_improvements = list(set(all_improvements))[:5]
    
    # Update session
    session.status = InterviewStatus.EVALUATED.value
    session.completed_at = datetime.now(timezone.utc)
    session.overall_score = percentage
    session.grade = grade
    session.relevance_score = (total_structure / num_questions) * 20 if num_questions else 0
    session.grammar_score = (total_grammar / num_questions) * 20 if num_questions else 0
    session.fluency_score = (total_fluency / num_questions) * 20 if num_questions else 0
    session.technical_score = (total_similarity / num_questions) * 20 if num_questions else 0
    session.strengths = overall_strengths
    session.weaknesses = overall_improvements
    session.summary = performance_summary
    
    # Save feedback
    feedback = InterviewFeedback(
        session_id=session.id,
        user_id=current_user.id,
        performance_rating=grade,
        executive_summary=performance_summary,
        communication_score=total_fluency / num_questions * 20 if num_questions else 0,
        technical_knowledge_score=total_similarity / num_questions * 20 if num_questions else 0,
        structure_score=total_structure / num_questions * 20 if num_questions else 0,
        strengths=[{"area": s, "description": s} for s in overall_strengths],
        weaknesses=[{"area": w, "description": w} for w in overall_improvements],
    )
    db.add(feedback)

    await db.commit()

    # Schedule audio file cleanup in background
    audio_paths = [q.audio_file_path for q in questions if q.audio_file_path]
    if audio_paths:
        background_tasks.add_task(cleanup_audio_files, session_id, audio_paths)

    return InterviewResult(
        session_id=session.id,
        technology=technology,
        difficulty=session.difficulty,
        question_scores=question_scores,
        total_grammar_score=round(total_grammar, 1),
        total_fluency_score=round(total_fluency, 1),
        total_structure_score=round(total_structure, 1),
        total_similarity_score=round(total_similarity, 1),
        total_score=round(total_score, 1),
        max_possible_score=round(max_possible, 1),
        percentage_score=round(percentage, 1),
        grade=grade,
        performance_summary=performance_summary,
        overall_strengths=overall_strengths,
        overall_improvements=overall_improvements,
        completed_at=session.completed_at
    )


@router.get(
    "/{session_id}/results",
    response_model=InterviewResult,
    summary="Get interview results",
    description="Get complete results for a submitted interview."
)
async def get_interview_results(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get results for a completed interview."""
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
            detail="Session not found"
        )
    
    if session.status not in [InterviewStatus.EVALUATED.value, InterviewStatus.COMPLETED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview not yet evaluated"
        )
    
    questions = sorted(session.questions, key=lambda q: q.question_order)
    technology = session.skills_tested[0] if session.skills_tested else "General"
    
    question_scores = []
    for q in questions:
        question_scores.append(QuestionScore(
            question_id=q.id,
            question_number=q.question_order,
            question_text=q.question_text,
            transcript=q.transcript or "",
            grammar_score=round((q.grammar_score or 0) / 20, 1),
            fluency_score=round((q.fluency_score or 0) / 20, 1),
            structure_score=round((q.relevance_score or 0) / 20, 1),
            similarity_score=round((q.keyword_score or 0) / 20, 1),
            overall_score=round((q.overall_score or 0) / 20, 1),
            strengths=q.strengths or [],
            improvements=q.weaknesses or [],
            ideal_answer=q.ideal_answer
        ))
    
    total_score = sum(qs.overall_score for qs in question_scores)
    max_possible = len(questions) * 5.0
    
    return InterviewResult(
        session_id=session.id,
        technology=technology,
        difficulty=session.difficulty,
        question_scores=question_scores,
        total_grammar_score=round(sum(qs.grammar_score for qs in question_scores), 1),
        total_fluency_score=round(sum(qs.fluency_score for qs in question_scores), 1),
        total_structure_score=round(sum(qs.structure_score for qs in question_scores), 1),
        total_similarity_score=round(sum(qs.similarity_score for qs in question_scores), 1),
        total_score=round(total_score, 1),
        max_possible_score=round(max_possible, 1),
        percentage_score=round(session.overall_score or 0, 1),
        grade=session.grade or "N/A",
        performance_summary=session.summary or "",
        overall_strengths=session.strengths or [],
        overall_improvements=session.weaknesses or [],
        completed_at=session.completed_at or datetime.now(timezone.utc)
    )


@router.get(
    "/history",
    response_model=InterviewHistoryResponse,
    summary="Get interview history",
    description="Get all completed interviews for the current user."
)
async def get_interview_history(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's interview history."""
    # Count total
    count_result = await db.execute(
        select(func.count(InterviewSession.id)).where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == InterviewStatus.EVALUATED.value
        )
    )
    total_count = count_result.scalar()
    
    # Get sessions
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == InterviewStatus.EVALUATED.value
        ).order_by(InterviewSession.completed_at.desc())
        .limit(limit).offset(offset)
    )
    sessions = result.scalars().all()
    
    history_items = []
    for session in sessions:
        technology = session.skills_tested[0] if session.skills_tested else "General"
        max_possible = session.total_questions * 5.0
        total_score = (session.overall_score or 0) * max_possible / 100
        
        history_items.append(InterviewHistoryItem(
            session_id=session.id,
            technology=technology,
            difficulty=session.difficulty,
            total_questions=session.total_questions,
            total_score=round(total_score, 1),
            max_possible_score=round(max_possible, 1),
            percentage_score=round(session.overall_score or 0, 1),
            grade=session.grade or "N/A",
            completed_at=session.completed_at or session.created_at
        ))
    
    return InterviewHistoryResponse(
        interviews=history_items,
        total_count=total_count
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def cleanup_audio_files(session_id: str, audio_paths: List[str]):
    """
    Background task to clean up audio files after processing.

    Args:
        session_id: Interview session ID
        audio_paths: List of audio file paths to delete
    """
    import shutil

    for path in audio_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
                logger.debug(f"Deleted audio file: {path}")
        except Exception as e:
            logger.warning(f"Failed to delete audio file {path}: {e}")

    # Try to remove the session directory if empty
    session_dir = os.path.join(settings.upload_dir, "audio", session_id)
    try:
        if os.path.exists(session_dir) and not os.listdir(session_dir):
            os.rmdir(session_dir)
            logger.debug(f"Deleted empty session directory: {session_dir}")
    except Exception as e:
        logger.warning(f"Failed to delete session directory {session_dir}: {e}")


def _get_fallback_questions(technology: str, num_questions: int, difficulty: str) -> list:
    """Get fallback questions when AI generation fails."""
    from app.services.question_service import GeneratedQuestion
    
    fallback_questions = {
        "python": [
            "What are Python's key features?",
            "Explain the difference between lists and tuples in Python.",
            "What are decorators in Python and how do they work?",
            "Explain the GIL (Global Interpreter Lock) in Python.",
            "What are generators and how are they different from regular functions?",
            "Explain the concept of context managers in Python.",
            "What is the difference between deep copy and shallow copy?",
            "How does Python's memory management work?",
        ],
        "javascript": [
            "What is the event loop in JavaScript?",
            "Explain closures in JavaScript.",
            "What is the difference between let, const, and var?",
            "Explain Promises and async/await in JavaScript.",
            "What is prototypal inheritance in JavaScript?",
            "Explain the concept of hoisting.",
            "What are arrow functions and how do they differ from regular functions?",
            "Explain the 'this' keyword in JavaScript.",
        ],
        "react": [
            "What is the Virtual DOM and how does React use it?",
            "Explain the difference between state and props.",
            "What are React Hooks and why were they introduced?",
            "How does useEffect work and when should you use it?",
            "Explain React's reconciliation algorithm.",
            "What is the Context API and when should you use it?",
            "How do you optimize React application performance?",
            "Explain the component lifecycle in React.",
        ],
    }
    
    tech_lower = technology.lower()
    questions_list = fallback_questions.get(tech_lower, [
        f"Explain the core concepts of {technology}.",
        f"What are the key features of {technology}?",
        f"How would you use {technology} in a real-world project?",
        f"What are the best practices when working with {technology}?",
        f"Explain a challenging problem you solved using {technology}.",
    ])
    
    # Select questions based on count
    selected = questions_list[:num_questions]
    
    return [
        GeneratedQuestion(
            question_text=q,
            category="technical",
            difficulty=difficulty,
            expected_topics=[technology.lower()],
            time_limit=120,
            follow_up_questions=[]
        )
        for q in selected
    ]


def _generate_ideal_answer(technology: str, question: str) -> str:
    """Generate a placeholder ideal answer."""
    tech_lower = technology.lower()
    
    # Check if we have a stored ideal answer
    if tech_lower in IDEAL_ANSWERS:
        for stored_q, stored_a in IDEAL_ANSWERS[tech_lower].items():
            if stored_q.lower() in question.lower() or question.lower() in stored_q.lower():
                return stored_a
    
    # Generic template
    return f"A comprehensive answer should include: 1) Clear definition or explanation of the concept, 2) How it works or is implemented, 3) Key benefits and use cases, 4) Best practices, 5) Real-world examples. For {technology}, focus on practical applications and technical accuracy."
