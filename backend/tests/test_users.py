"""
Tests for User API endpoints

Tests cover:
- User registration
- User login
- Get current user profile
- Update profile
"""

import pytest
from httpx import AsyncClient


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email fails."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "email": "test@example.com",  # Already exists from test_user fixture
                "password": "anotherpassword123",
                "full_name": "Another User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format fails."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "email": "not-an-email",
                "password": "securepassword123",
                "full_name": "Bad Email User"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/users/register",
            json={
                "email": "shortpass@example.com",
                "password": "short",
                "full_name": "Short Pass User"
            }
        )
        
        assert response.status_code == 422


class TestUserLogin:
    """Tests for user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/v1/users/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/v1/users/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/v1/users/login",
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == 401


class TestUserProfile:
    """Tests for user profile endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_profile_authenticated(self, client: AsyncClient, test_user, auth_headers):
        """Test getting profile when authenticated."""
        response = await client.get(
            "/api/v1/users/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client: AsyncClient):
        """Test getting profile without authentication fails."""
        response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, test_user, auth_headers):
        """Test updating user profile."""
        response = await client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "full_name": "Updated Name",
                "target_role": "Senior Developer"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["target_role"] == "Senior Developer"
    
    @pytest.mark.asyncio
    async def test_update_skills(self, client: AsyncClient, test_user, auth_headers):
        """Test updating user skills."""
        response = await client.put(
            "/api/v1/users/me/skills",
            headers=auth_headers,
            json={
                "skills": ["Python", "JavaScript", "React", "FastAPI"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Python" in data["skills"]
        assert "React" in data["skills"]
        assert len(data["skills"]) == 4
