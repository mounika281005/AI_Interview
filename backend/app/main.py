"""
==============================================================================
AI Mock Interview System - Main Application
==============================================================================

FastAPI application entry point with router registration, middleware setup,
and lifecycle event handlers.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, drop_db
from app.routers import users_router, interviews_router, feedback_router, skill_interview_router

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =============================================================================
# LIFESPAN CONTEXT MANAGER
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # -------------------------------------------------------------------------
    # STARTUP
    # -------------------------------------------------------------------------
    logger.info("🚀 Starting AI Mock Interview System...")
    
    # Initialize database
    logger.info("📦 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized successfully")
    
    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info(f"📁 Upload directory ready: {settings.upload_dir}")
    
    # Log configuration
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"🔧 Debug Mode: {settings.debug}")
    
    logger.info("✅ Application started successfully!")
    
    yield
    
    # -------------------------------------------------------------------------
    # SHUTDOWN
    # -------------------------------------------------------------------------
    logger.info("🛑 Shutting down AI Mock Interview System...")
    logger.info("✅ Application shutdown complete")


# =============================================================================
# APPLICATION INSTANCE
# =============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    redirect_slashes=False,
    description="""
    # AI Mock Interview System API
    
    A comprehensive API for conducting AI-powered mock interviews with 
    NLP-based evaluation and personalized feedback.
    
    ## Features
    
    - 👤 **User Management**: Registration, authentication, profile management
    - 📝 **Question Generation**: AI-generated interview questions
    - 🎤 **Audio Processing**: Upload and process voice responses
    - 🗣️ **Speech-to-Text**: Convert audio to text transcripts
    - 📊 **NLP Evaluation**: Analyze responses for relevance, grammar, fluency
    - 💯 **Scoring**: Calculate comprehensive scores
    - 📋 **Feedback**: Generate personalized improvement suggestions
    - 📈 **Dashboard**: Track progress and performance trends
    
    ## Authentication
    
    Most endpoints require a JWT bearer token. Get one by:
    1. Register at `/users/register`
    2. Login at `/users/login`
    3. Include token in Authorization header: `Bearer <token>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS Middleware - Must be added first
# In production, restrict origins to your actual frontend domains
cors_origins = settings.cors_origins_list if settings.is_production() else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.is_production(),  # Enable credentials in production with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"➡ {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        logger.info(f"⬅ {request.method} {request.url.path} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request error: {request.method} {request.url.path} - {e}")
        raise


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            },
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    # Don't expose internal error details in production
    message = str(exc) if settings.debug else "An unexpected error occurred"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": message
            },
            "data": None
        }
    )


# =============================================================================
# ROUTER REGISTRATION
# =============================================================================

# API v1 prefix
API_V1_PREFIX = "/api/v1"

# Register routers (routers already have their own prefix like /users, /interviews)
app.include_router(
    users_router,
    prefix=API_V1_PREFIX,
    tags=["Users"]
)

app.include_router(
    interviews_router,
    prefix=API_V1_PREFIX,
    tags=["Interviews"]
)

app.include_router(
    feedback_router,
    prefix=API_V1_PREFIX,
    tags=["Feedback & Analytics"]
)

app.include_router(
    skill_interview_router,
    prefix=API_V1_PREFIX,
    tags=["Skill-Based Interview"]
)


# =============================================================================
# STATIC FILES (for audio uploads)
# =============================================================================

# Mount uploads directory for serving audio files
if os.path.exists(settings.upload_dir):
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.upload_dir),
        name="uploads"
    )


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message.
    
    Returns basic API information and links to documentation.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API health status for monitoring.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/api/v1", tags=["Root"])
async def api_root():
    """
    API v1 root endpoint.
    
    Returns available endpoints and API information.
    """
    return {
        "version": "1.0.0",
        "endpoints": {
            "users": f"{API_V1_PREFIX}/users",
            "interviews": f"{API_V1_PREFIX}/interviews",
            "feedback": f"{API_V1_PREFIX}/feedback",
            "skill_interview": f"{API_V1_PREFIX}/skill-interview"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower()
    )
