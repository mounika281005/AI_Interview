"""
Question Generation Service API

FastAPI service that exposes the question generator functionality
via REST API endpoints.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import asyncio

# Import from our generator module
# from generators.question_generator import (
#     QuestionGenerator, GeneratorInput, ExperienceLevel, OpenAIProvider
# )

app = FastAPI(
    title="Interview Question Generator API",
    description="AI-powered role-specific interview question generation",
    version="1.0.0"
)


# =============================================================================
# API MODELS
# =============================================================================

class ExperienceLevelEnum(str, Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"
    lead = "lead"


class QuestionGenerationRequest(BaseModel):
    """Request model for question generation."""
    job_role: str = Field(..., example="Senior Backend Engineer")
    skills: List[str] = Field(..., example=["Python", "FastAPI", "PostgreSQL"])
    experience_level: ExperienceLevelEnum = Field(..., example="senior")
    num_technical: int = Field(default=5, ge=1, le=10)
    num_hr: int = Field(default=3, ge=1, le=5)
    num_scenario: int = Field(default=2, ge=1, le=5)
    industry: Optional[str] = Field(default="Technology", example="FinTech")
    company_values: Optional[List[str]] = Field(
        default=["Innovation", "Collaboration"],
        example=["Innovation", "Security"]
    )
    interview_duration_minutes: Optional[int] = Field(default=60, ge=30, le=120)

    class Config:
        json_schema_extra = {
            "example": {
                "job_role": "Senior Backend Engineer",
                "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
                "experience_level": "senior",
                "num_technical": 5,
                "num_hr": 3,
                "num_scenario": 2,
                "industry": "FinTech",
                "company_values": ["Innovation", "Security", "Customer Focus"],
                "interview_duration_minutes": 60
            }
        }


class TechnicalQuestionResponse(BaseModel):
    """Response model for technical questions."""
    id: int
    question: str
    category: str
    skill_tested: str
    difficulty: str
    expected_points: List[str]
    follow_up: str
    time_minutes: int
    evaluation_criteria: dict


class HRQuestionResponse(BaseModel):
    """Response model for HR questions."""
    id: int
    question: str
    competency: str
    star_focus: str
    positive_indicators: List[str]
    red_flags: List[str]
    follow_up_probes: List[str]
    time_minutes: int


class ScenarioQuestionResponse(BaseModel):
    """Response model for scenario questions."""
    id: int
    scenario: str
    question: str
    type: str
    skills_tested: List[str]
    decision_points: List[str]
    acceptable_approaches: List[dict]
    excellent_response_traits: List[str]
    time_minutes: int


class QuestionGenerationResponse(BaseModel):
    """Complete response for question generation."""
    job_role: str
    experience_level: str
    technical_questions: List[TechnicalQuestionResponse]
    hr_questions: List[HRQuestionResponse]
    scenario_questions: List[ScenarioQuestionResponse]
    total_time_minutes: int
    generation_metadata: dict


class FollowUpRequest(BaseModel):
    """Request for generating follow-up questions."""
    original_question: str
    candidate_response: str
    skills: List[str]
    identified_gaps: Optional[List[str]] = []


class FollowUpResponse(BaseModel):
    """Response for follow-up question."""
    question: str
    purpose: str
    target_area: str
    expected_insight: str


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.post(
    "/api/questions/generate",
    response_model=QuestionGenerationResponse,
    summary="Generate Interview Questions",
    description="Generate a complete set of role-specific interview questions"
)
async def generate_questions(request: QuestionGenerationRequest):
    """
    Generate technical, HR, and scenario-based interview questions
    tailored to the specified job role, skills, and experience level.
    
    - **job_role**: The target position (e.g., "Senior Backend Engineer")
    - **skills**: List of required skills to test
    - **experience_level**: entry, mid, senior, or lead
    - **num_technical**: Number of technical questions (1-10)
    - **num_hr**: Number of HR/behavioral questions (1-5)
    - **num_scenario**: Number of scenario questions (1-5)
    """
    try:
        # In production, this would call the actual generator
        # generator = QuestionGenerator(llm_provider=get_llm_provider())
        # result = await generator.generate(GeneratorInput(**request.dict()))
        
        # For now, return mock response structure
        return {
            "job_role": request.job_role,
            "experience_level": request.experience_level.value,
            "technical_questions": [],
            "hr_questions": [],
            "scenario_questions": [],
            "total_time_minutes": 0,
            "generation_metadata": {
                "skills_covered": request.skills,
                "industry": request.industry
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/questions/follow-up",
    response_model=FollowUpResponse,
    summary="Generate Follow-up Question",
    description="Generate a follow-up question based on candidate's response"
)
async def generate_followup(request: FollowUpRequest):
    """
    Generate a contextual follow-up question based on the candidate's
    response to probe deeper or clarify gaps.
    """
    try:
        # In production, this would call the LLM
        return {
            "question": "Can you elaborate on...",
            "purpose": "probe",
            "target_area": "technical depth",
            "expected_insight": "Understanding of implementation details"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/questions/templates",
    summary="Get Question Templates",
    description="Get available question templates by category"
)
async def get_templates(category: Optional[str] = None):
    """
    Retrieve question templates that can be customized.
    Optionally filter by category: technical, hr, scenario
    """
    templates = {
        "technical": [
            "Explain the concept of {skill} and its use cases",
            "Design a system that handles {requirement}",
            "Debug this {skill} problem: {problem_description}"
        ],
        "hr": [
            "Tell me about a time when you {competency_action}",
            "Describe a situation where you had to {challenge}",
            "How do you handle {situation}?"
        ],
        "scenario": [
            "You're faced with {scenario}. How would you approach it?",
            "Given {constraints}, what would your solution be?",
            "Walk me through handling {critical_situation}"
        ]
    }
    
    if category:
        return {category: templates.get(category, [])}
    return templates


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "question-generator"}


# =============================================================================
# STARTUP
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
