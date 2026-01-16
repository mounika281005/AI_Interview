"""
==============================================================================
AI Mock Interview System - Routers Package
==============================================================================

This package exports all API routers for the FastAPI application.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from app.routers.users import router as users_router
from app.routers.interviews import router as interviews_router
from app.routers.feedback import router as feedback_router
from app.routers.skill_interview import router as skill_interview_router

__all__ = [
    "users_router",
    "interviews_router",
    "feedback_router",
    "skill_interview_router",
]
