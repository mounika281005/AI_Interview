"""
==============================================================================
AI Mock Interview System - User API Router
==============================================================================

REST API endpoints for user management:
- User registration and authentication
- Profile management (CRUD)
- User statistics

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime, timedelta
from typing import List, Optional
import os
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserProfileResponse,
    UserStatsResponse,
    Token,
)
from app.schemas.common import APIResponse
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import settings

# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        404: {"description": "User not found"},
        401: {"description": "Not authenticated"},
    }
)


# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with profile information."
)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    **Request Body:**
    - **email**: Valid email address (unique)
    - **password**: Password (min 8 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **job_role**: Target job role (optional)
    - **skills**: List of skills (optional)
    - **experience_years**: Years of experience (optional)
    
    **Returns:**
    - JWT access token
    - User profile information
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        job_role=user_data.job_role,
        skills=user_data.skills or [],
        experience_years=user_data.experience_years or 0,
        experience_level=user_data.experience_level or "entry",
        industry=user_data.industry,
        bio=user_data.bio,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate access token
    access_token = create_access_token(subject=new_user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(new_user)
    )


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user and return JWT token."
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    **Request Body:**
    - **email**: User's email
    - **password**: User's password
    
    **Returns:**
    - JWT access token
    - User profile information
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Generate access token
    access_token = create_access_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user)
    )


# =============================================================================
# PROFILE ENDPOINTS
# =============================================================================

@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the authenticated user's profile."
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's profile.
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:** Complete user profile including:
    - Basic info (name, email, phone)
    - Professional details (role, skills, experience)
    - Statistics (interviews, scores)
    - Preferences
    """
    return UserProfileResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the authenticated user's profile."
)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's profile.
    
    **Request Body:** (all fields optional)
    - **first_name**: Updated first name
    - **last_name**: Updated last name
    - **job_role**: Updated target job role
    - **skills**: Updated skills list
    - **experience_years**: Updated experience
    - **experience_level**: entry/junior/mid/senior/lead
    - **bio**: Updated bio
    
    **Returns:** Updated user profile
    """
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    return UserProfileResponse.model_validate(current_user)


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics",
    description="Get the current user's interview statistics."
)
async def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive statistics for the current user.
    
    **Returns:**
    - Total interviews completed
    - Average and best scores
    - Performance trends
    - Strengths and areas to improve
    """
    # Import here to avoid circular imports
    from app.services.stats_service import calculate_user_stats
    
    stats = await calculate_user_stats(current_user.id, db)
    return stats


# =============================================================================
# USER CRUD (Admin/Public endpoints)
# =============================================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a user's public profile by their ID."
)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a user's public profile by ID.
    
    **Path Parameters:**
    - **user_id**: The user's unique identifier
    
    **Returns:** Public user profile
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.model_validate(user)


@router.delete(
    "/me",
    response_model=APIResponse,
    summary="Delete current user account",
    description="Permanently delete the current user's account."
)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete the current user's account.
    
    **Warning:** This action is irreversible and will delete:
    - User profile
    - All interview sessions
    - All feedback and scores
    
    **Returns:** Confirmation message
    """
    await db.delete(current_user)
    await db.commit()
    
    return APIResponse(
        success=True,
        message="Account deleted successfully"
    )


# =============================================================================
# SKILL MANAGEMENT
# =============================================================================

@router.post(
    "/me/skills",
    response_model=UserProfileResponse,
    summary="Add skills to profile",
    description="Add new skills to the user's profile."
)
async def add_skills(
    skills: List[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add skills to the current user's profile.
    
    **Request Body:** List of skill names
    
    **Returns:** Updated user profile
    """
    current_skills = set(current_user.skills or [])
    current_skills.update(skills)
    current_user.skills = list(current_skills)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserProfileResponse.model_validate(current_user)


@router.delete(
    "/me/skills/{skill}",
    response_model=UserProfileResponse,
    summary="Remove a skill",
    description="Remove a skill from the user's profile."
)
async def remove_skill(
    skill: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a skill from the current user's profile.
    
    **Path Parameters:**
    - **skill**: The skill name to remove
    
    **Returns:** Updated user profile
    """
    if current_user.skills and skill in current_user.skills:
        current_user.skills.remove(skill)
        await db.commit()
        await db.refresh(current_user)

    return UserProfileResponse.model_validate(current_user)


# =============================================================================
# RESUME MANAGEMENT
# =============================================================================

@router.post(
    "/me/resume",
    response_model=APIResponse,
    summary="Upload and parse resume",
    description="Upload a resume file (PDF/TXT/DOCX) and extract structured information."
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF, TXT, or DOCX)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse a resume file.

    **Request:**
    - **file**: Resume file (PDF, TXT, or DOCX format)

    **Process:**
    1. Validates file type
    2. Saves file temporarily
    3. Extracts text and structured information
    4. Updates user profile with extracted data

    **Returns:**
    - Success message
    - Parsed resume data
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.text', '.doc', '.docx'}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )

    try:
        # Create upload directory if not exists
        upload_dir = "uploads/resumes"
        os.makedirs(upload_dir, exist_ok=True)

        # Save file with unique name
        unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, 'wb') as f:
            f.write(content)

        # Parse resume
        from app.services.resume_service import ResumeParsingService
        resume_service = ResumeParsingService()
        parsed_data = await resume_service.parse_resume(file_path, file.filename)

        # Update user profile with parsed data
        current_user.resume_url = f"/uploads/resumes/{unique_filename}"
        current_user.resume_data = parsed_data

        # Auto-update skills if extracted
        if parsed_data.get("extracted_skills"):
            current_skills = set(current_user.skills or [])
            current_skills.update(parsed_data["extracted_skills"][:20])  # Limit to top 20
            current_user.skills = list(current_skills)

        # Auto-update experience years if calculated
        if parsed_data.get("total_years_experience"):
            current_user.experience_years = parsed_data["total_years_experience"]

        current_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(current_user)

        return APIResponse(
            success=True,
            message="Resume uploaded and parsed successfully",
            data={
                "file_name": file.filename,
                "parsed_data": parsed_data,
                "skills_extracted": len(parsed_data.get("extracted_skills", [])),
                "experience_found": parsed_data.get("total_years_experience", 0)
            }
        )

    except Exception as e:
        # Clean up file if parsing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume: {str(e)}"
        )


@router.get(
    "/me/resume",
    response_model=APIResponse,
    summary="Get parsed resume data",
    description="Retrieve the user's parsed resume information."
)
async def get_resume_data(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's parsed resume data.

    **Returns:**
    - Parsed resume information including:
      - Extracted skills
      - Work experience
      - Education
      - Projects
      - Certifications
    """
    if not current_user.resume_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded yet"
        )

    return APIResponse(
        success=True,
        message="Resume data retrieved successfully",
        data=current_user.resume_data
    )


@router.delete(
    "/me/resume",
    response_model=APIResponse,
    summary="Delete resume",
    description="Remove the user's uploaded resume and parsed data."
)
async def delete_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete the user's resume and parsed data.

    **Returns:** Confirmation message
    """
    if not current_user.resume_data and not current_user.resume_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume to delete"
        )

    # Delete file if exists
    if current_user.resume_url:
        file_path = current_user.resume_url.lstrip('/')
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete resume file: {e}")

    # Clear resume data
    current_user.resume_url = None
    current_user.resume_data = None
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return APIResponse(
        success=True,
        message="Resume deleted successfully"
    )
