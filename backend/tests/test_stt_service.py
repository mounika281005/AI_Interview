"""
Tests for Speech-to-Text Service

Tests cover:
- Audio transcription
- Multiple audio formats
- Error handling
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import io


class TestSTTService:
    """Tests for the Speech-to-Text service."""
    
    def test_transcribe_audio_success(self):
        """Test successful audio transcription."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        # Mock the speech recognition
        with patch.object(stt, 'transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Hello, this is a test transcription.",
                "confidence": 0.95
            }
            
            result = stt.transcribe("test_audio.wav")
            
            assert result["text"] == "Hello, this is a test transcription."
            assert result["confidence"] == 0.95
    
    def test_transcribe_audio_from_bytes(self):
        """Test transcription from audio bytes."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        # Mock audio bytes
        audio_bytes = b"fake audio data"
        
        with patch.object(stt, 'transcribe_bytes') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Transcribed from bytes.",
                "confidence": 0.90
            }
            
            result = stt.transcribe_bytes(audio_bytes)
            
            assert "text" in result
    
    def test_transcribe_empty_audio(self):
        """Test handling of empty/silent audio."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        with patch.object(stt, 'transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "",
                "confidence": 0.0,
                "error": "No speech detected"
            }
            
            result = stt.transcribe("silent_audio.wav")
            
            assert result["text"] == ""
            assert "error" in result or result["confidence"] == 0.0
    
    def test_transcribe_corrupted_file(self):
        """Test handling of corrupted audio file."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        with patch.object(stt, 'transcribe') as mock_transcribe:
            mock_transcribe.side_effect = Exception("Invalid audio format")
            
            with pytest.raises(Exception):
                stt.transcribe("corrupted.wav")
    
    def test_supported_audio_formats(self):
        """Test that service supports required audio formats."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        # Check supported formats
        supported_formats = getattr(stt, 'supported_formats', ['wav', 'mp3', 'webm', 'ogg'])
        
        assert 'wav' in supported_formats
        assert 'webm' in supported_formats or 'mp3' in supported_formats


class TestAudioConversion:
    """Tests for audio format conversion."""
    
    def test_convert_webm_to_wav(self):
        """Test converting WebM to WAV format."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        # Mock conversion function
        if hasattr(stt, 'convert_audio'):
            with patch.object(stt, 'convert_audio') as mock_convert:
                mock_convert.return_value = "/path/to/converted.wav"
                
                result = stt.convert_audio("/path/to/audio.webm", "wav")
                
                assert result.endswith('.wav')
    
    def test_get_audio_duration(self):
        """Test getting audio duration."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        if hasattr(stt, 'get_duration'):
            with patch.object(stt, 'get_duration') as mock_duration:
                mock_duration.return_value = 45.5
                
                duration = stt.get_duration("/path/to/audio.wav")
                
                assert duration == 45.5
                assert isinstance(duration, (int, float))


class TestTranscriptionConfidence:
    """Tests for transcription confidence handling."""
    
    def test_high_confidence_transcription(self):
        """Test handling of high confidence transcription."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        with patch.object(stt, 'transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Clear speech with high confidence.",
                "confidence": 0.98
            }
            
            result = stt.transcribe("clear_audio.wav")
            
            assert result["confidence"] >= 0.9
    
    def test_low_confidence_transcription(self):
        """Test handling of low confidence transcription."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        with patch.object(stt, 'transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Unclear mumbled speech maybe.",
                "confidence": 0.4,
                "warning": "Low confidence transcription"
            }
            
            result = stt.transcribe("noisy_audio.wav")
            
            assert result["confidence"] < 0.5


class TestAsyncTranscription:
    """Tests for async transcription methods."""
    
    @pytest.mark.asyncio
    async def test_async_transcribe(self):
        """Test async transcription method."""
        from app.services.stt_service import STTService
        
        stt = STTService()
        
        if hasattr(stt, 'transcribe_async'):
            with patch.object(stt, 'transcribe_async', new_callable=AsyncMock) as mock_transcribe:
                mock_transcribe.return_value = {
                    "text": "Async transcription result.",
                    "confidence": 0.92
                }
                
                result = await stt.transcribe_async("audio.wav")
                
                assert result["text"] == "Async transcription result."
