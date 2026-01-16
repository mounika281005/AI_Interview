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
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

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
    
    stats = await calculate_user_stats(db, current_user.id)
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
