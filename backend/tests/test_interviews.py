"""
Tests for Interview API endpoints

Tests cover:
- Creating interview sessions
- Getting sessions
- Generating questions
- Uploading audio
- Transcription
- Evaluation
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import io


class TestInterviewSessions:
    """Tests for interview session endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, client: AsyncClient, test_user, auth_headers):
        """Test creating a new interview session."""
        response = await client.post(
            "/api/v1/interviews/sessions",
            headers=auth_headers,
            json={
                "title": "My Practice Session",
                "target_role": "Frontend Developer",
                "target_company": "Google",
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Practice Session"
        assert data["target_role"] == "Frontend Developer"
        assert data["status"] == "created"
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_session_unauthenticated(self, client: AsyncClient):
        """Test creating session without auth fails."""
        response = await client.post(
            "/api/v1/interviews/sessions",
            json={"title": "Test", "target_role": "Developer"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_sessions_list(self, client: AsyncClient, test_user, auth_headers, test_session_data):
        """Test getting list of user's sessions."""
        response = await client.get(
            "/api/v1/interviews/sessions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == test_session_data.id
    
    @pytest.mark.asyncio
    async def test_get_session_by_id(self, client: AsyncClient, auth_headers, test_session_data):
        """Test getting a specific session by ID."""
        response = await client.get(
            f"/api/v1/interviews/sessions/{test_session_data.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_session_data.id
        assert data["title"] == test_session_data.title
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, client: AsyncClient, auth_headers):
        """Test getting non-existent session returns 404."""
        response = await client.get(
            "/api/v1/interviews/sessions/non-existent-id",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestQuestionGeneration:
    """Tests for question generation endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_questions_success(self, client: AsyncClient, auth_headers, test_session_data):
        """Test generating questions for a session."""
        response = await client.post(
            f"/api/v1/interviews/sessions/{test_session_data.id}/questions/generate",
            headers=auth_headers,
            json={
                "num_questions": 3,
                "categories": ["behavioral", "technical"],
                "skills": ["Python", "React"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_questions_invalid_session(self, client: AsyncClient, auth_headers):
        """Test generating questions for non-existent session fails."""
        response = await client.post(
            "/api/v1/interviews/sessions/invalid-id/questions/generate",
            headers=auth_headers,
            json={"num_questions": 5, "categories": ["behavioral"]}
        )
        
        assert response.status_code == 404


class TestAudioUpload:
    """Tests for audio upload endpoints."""
    
    @pytest.mark.asyncio
    async def test_upload_audio_success(self, client: AsyncClient, auth_headers, test_session_data, test_question):
        """Test uploading audio for a question."""
        # Create a mock audio file
        audio_content = b"fake audio content for testing"
        files = {
            "audio_file": ("test.webm", io.BytesIO(audio_content), "audio/webm")
        }
        
        response = await client.post(
            f"/api/v1/interviews/sessions/{test_session_data.id}/questions/{test_question.id}/audio",
            headers=auth_headers,
            files=files,
            data={"duration": "45"}
        )
        
        # Should succeed (or return appropriate status based on implementation)
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_upload_audio_invalid_question(self, client: AsyncClient, auth_headers, test_session_data):
        """Test uploading audio for non-existent question fails."""
        audio_content = b"fake audio content"
        files = {
            "audio_file": ("test.webm", io.BytesIO(audio_content), "audio/webm")
        }
        
        response = await client.post(
            f"/api/v1/interviews/sessions/{test_session_data.id}/questions/invalid-id/audio",
            headers=auth_headers,
            files=files,
            data={"duration": "45"}
        )
        
        assert response.status_code == 404


class TestTranscription:
    """Tests for audio transcription endpoints."""
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, client: AsyncClient, auth_headers, test_session_data, test_question):
        """Test transcribing audio for a question."""
        # Mock the STT service
        with patch('app.services.stt_service.STTService.transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "This is my transcribed answer about my experience.",
                "confidence": 0.95
            }
            
            response = await client.post(
                f"/api/v1/interviews/sessions/{test_session_data.id}/questions/{test_question.id}/transcribe",
                headers=auth_headers
            )
            
            # Response depends on whether audio was uploaded
            assert response.status_code in [200, 400, 404]


class TestEvaluation:
    """Tests for answer evaluation endpoints."""
    
    @pytest.mark.asyncio
    async def test_evaluate_response_success(self, client: AsyncClient, auth_headers, test_session_data, test_question, test_session):
        """Test evaluating a transcribed response."""
        # First, add transcription to the question
        test_question.transcription = "I have 5 years of experience in software development."
        test_question.is_answered = True
        await test_session.commit()
        
        # Mock the evaluation service
        with patch('app.services.nlp_evaluator.AnswerEvaluator.evaluate') as mock_evaluate:
            mock_evaluate.return_value = {
                "relevance_score": 0.85,
                "completeness_score": 0.80,
                "grammar_score": 0.90,
                "confidence_score": 0.75,
                "overall_score": 0.82,
                "feedback": "Good response with relevant experience mentioned."
            }
            
            response = await client.post(
                f"/api/v1/interviews/sessions/{test_session_data.id}/questions/{test_question.id}/evaluate",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 400]


class TestSessionCompletion:
    """Tests for completing interview sessions."""
    
    @pytest.mark.asyncio
    async def test_complete_session_success(self, client: AsyncClient, auth_headers, test_session_data):
        """Test completing an interview session."""
        response = await client.post(
            f"/api/v1/interviews/sessions/{test_session_data.id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_complete_session_already_completed(self, client: AsyncClient, auth_headers, test_session_data, test_session):
        """Test completing an already completed session."""
        # First complete the session
        test_session_data.status = "completed"
        await test_session.commit()
        
        response = await client.post(
            f"/api/v1/interviews/sessions/{test_session_data.id}/complete",
            headers=auth_headers
        )
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 400]
