"""
==============================================================================
AI Mock Interview System - Authentication Service
==============================================================================

Handles authentication, password hashing, and JWT token management.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db

# =============================================================================
# PASSWORD HASHING
# =============================================================================


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    # bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    # bcrypt has a 72-byte limit, truncate to match hashing
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        User ID (subject) if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return user_id
    
    except JWTError:
        return None


# =============================================================================
# AUTHENTICATION DEPENDENCY
# =============================================================================

# Security scheme for swagger docs
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency to get the current authenticated user.
    
    Usage in routes:
        @router.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user": user.email}
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException: If authentication fails
    """
    # Import here to avoid circular imports
    from app.models.user import User
    import logging
    logger = logging.getLogger(__name__)

    logger.debug("Authenticating user...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency to ensure user is active.
    
    Args:
        current_user: User from get_current_user dependency
    
    Returns:
        Active user object
    
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# =============================================================================
# OPTIONAL AUTHENTICATION
# =============================================================================

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Optional authentication - returns user if authenticated, None otherwise.
    
    Useful for routes that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Optional bearer token
        db: Database session
    
    Returns:
        User object or None
    """
    from app.models.user import User
    
    if credentials is None:
        return None
    
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        return None
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
