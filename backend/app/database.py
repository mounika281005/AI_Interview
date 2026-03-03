"""
==============================================================================
AI Mock Interview System - Database Configuration
==============================================================================

This module sets up the async SQLAlchemy database connection and session
management for the FastAPI application.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.config import settings


# ==============================================================================
# DATABASE ENGINE CONFIGURATION
# ==============================================================================

# Create async engine based on database URL
if "sqlite" in settings.database_url:
    # SQLite configuration (for development)
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,  # Log SQL queries in debug mode
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other databases (for production)
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,  # Check connection health
        pool_size=10,
        max_overflow=20,
    )


# ==============================================================================
# SESSION FACTORY
# ==============================================================================

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ==============================================================================
# BASE MODEL CLASS
# ==============================================================================

# Base class for all SQLAlchemy models
Base = declarative_base()


# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage in FastAPI routes:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ==============================================================================
# DATABASE INITIALIZATION
# ==============================================================================

async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Call this on application startup:
        @app.on_event("startup")
        async def startup():
            await init_db()
    """
    # Import all models to ensure they're registered with Base
    from app.models import user, interview, question, feedback  # noqa

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data!
    Only use in development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is successful, False otherwise
    """
    from sqlalchemy import text

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
