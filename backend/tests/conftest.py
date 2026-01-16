"""
Pytest Configuration and Fixtures

This module provides test fixtures for all test modules.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime
from uuid import uuid4

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers for a test user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_session_data(test_session: AsyncSession, test_user: User) -> InterviewSession:
    """Create a test interview session."""
    session = InterviewSession(
        id=str(uuid4()),
        user_id=test_user.id,
        title="Test Interview Session",
        target_role="Software Engineer",
        target_company="Test Company",
        difficulty="medium",
        status="created",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    test_session.add(session)
    await test_session.commit()
    await test_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def test_question(test_session: AsyncSession, test_session_data: InterviewSession) -> InterviewQuestion:
    """Create a test interview question."""
    question = InterviewQuestion(
        id=str(uuid4()),
        session_id=test_session_data.id,
        question_text="Tell me about yourself.",
        category="behavioral",
        difficulty="easy",
        order_index=0,
        time_limit=120,
        expected_topics=["background", "experience", "skills"],
        is_answered=False,
        created_at=datetime.utcnow(),
    )
    test_session.add(question)
    await test_session.commit()
    await test_session.refresh(question)
    return question
