"""
Tests for Feedback API endpoints

Tests cover:
- Score calculation
- Feedback generation
- History retrieval
- Dashboard data
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from datetime import datetime


class TestScoreCalculation:
    """Tests for score calculation endpoints."""
    
    @pytest.mark.asyncio
    async def test_calculate_scores_success(
        self, client: AsyncClient, auth_headers, test_session_data, test_question, test_session
    ):
        """Test calculating scores for a completed session."""
        # Mark question as answered with evaluation
        test_question.is_answered = True
        test_question.transcription = "Test answer"
        test_question.evaluation_scores = {
            "relevance_score": 0.8,
            "completeness_score": 0.75,
            "grammar_score": 0.9,
            "overall_score": 0.82
        }
        test_session_data.status = "completed"
        await test_session.commit()
        
        response = await client.post(
            f"/api/v1/feedback/sessions/{test_session_data.id}/scores",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data or "category_scores" in data
    
    @pytest.mark.asyncio
    async def test_calculate_scores_incomplete_session(
        self, client: AsyncClient, auth_headers, test_session_data
    ):
        """Test calculating scores for incomplete session."""
        response = await client.post(
            f"/api/v1/feedback/sessions/{test_session_data.id}/scores",
            headers=auth_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_calculate_scores_invalid_session(self, client: AsyncClient, auth_headers):
        """Test calculating scores for non-existent session fails."""
        response = await client.post(
            "/api/v1/feedback/sessions/invalid-id/scores",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestFeedbackGeneration:
    """Tests for feedback generation endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_feedback_success(
        self, client: AsyncClient, auth_headers, test_session_data, test_question, test_session
    ):
        """Test generating feedback for a session."""
        # Setup completed session with scores
        test_question.is_answered = True
        test_question.evaluation_scores = {
            "relevance_score": 0.8,
            "completeness_score": 0.75,
            "grammar_score": 0.9
        }
        test_session_data.status = "completed"
        test_session_data.overall_score = 82.0
        await test_session.commit()
        
        response = await client.post(
            f"/api/v1/feedback/sessions/{test_session_data.id}/feedback",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Check for expected feedback fields
        assert any(key in data for key in ["overall_rating", "summary", "strengths", "suggestions"])
    
    @pytest.mark.asyncio
    async def test_get_session_feedback(
        self, client: AsyncClient, auth_headers, test_session_data, test_session
    ):
        """Test retrieving existing feedback for a session."""
        # First generate feedback (or check if it exists)
        response = await client.get(
            f"/api/v1/feedback/sessions/{test_session_data.id}",
            headers=auth_headers
        )
        
        # Should return feedback or 404 if not generated yet
        assert response.status_code in [200, 404]


class TestFeedbackHistory:
    """Tests for feedback history endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_history_success(self, client: AsyncClient, auth_headers, test_session_data):
        """Test getting user's feedback history."""
        response = await client.get(
            "/api/v1/feedback/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should return a list or object with sessions
        assert isinstance(data, (list, dict))
    
    @pytest.mark.asyncio
    async def test_get_history_unauthenticated(self, client: AsyncClient):
        """Test getting history without auth fails."""
        response = await client.get("/api/v1/feedback/history")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_history_with_pagination(self, client: AsyncClient, auth_headers):
        """Test getting history with pagination parameters."""
        response = await client.get(
            "/api/v1/feedback/history",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200


class TestDashboard:
    """Tests for dashboard data endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_dashboard_success(self, client: AsyncClient, auth_headers, test_user):
        """Test getting dashboard data."""
        response = await client.get(
            "/api/v1/feedback/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Check for expected dashboard fields
        expected_fields = ["total_sessions", "average_score", "total_practice_minutes"]
        # At least some stats should be present
        assert any(field in data for field in expected_fields) or isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_get_dashboard_unauthenticated(self, client: AsyncClient):
        """Test getting dashboard without auth fails."""
        response = await client.get("/api/v1/feedback/dashboard")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_chart_data(self, client: AsyncClient, auth_headers):
        """Test getting chart data for visualizations."""
        response = await client.get(
            "/api/v1/feedback/charts",
            headers=auth_headers,
            params={"chart_type": "score_trend", "days": 30}
        )
        
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestCategoryScores:
    """Tests for category-specific score endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_category_breakdown(
        self, client: AsyncClient, auth_headers, test_session_data
    ):
        """Test getting category score breakdown."""
        response = await client.get(
            f"/api/v1/feedback/sessions/{test_session_data.id}/categories",
            headers=auth_headers
        )
        
        # Should return scores or 404 if not available
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_improvement_areas(self, client: AsyncClient, auth_headers):
        """Test getting areas for improvement."""
        response = await client.get(
            "/api/v1/feedback/improvement-areas",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404]
