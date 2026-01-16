"""
==============================================================================
AI Mock Interview System - Speech-to-Text Service
==============================================================================

Handles audio transcription using Hugging Face API, OpenAI Whisper API, 
or local Whisper model.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
import asyncio
import logging
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def debug_log(msg: str, data: Any = None):
    """Helper for consistent debug logging."""
    if data is not None:
        logger.debug(f"{msg}: {data}")
    else:
        logger.debug(msg)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    text: str
    language: str
    duration: float
    confidence: float
    word_timestamps: Optional[list] = None
    segments: Optional[list] = None


# =============================================================================
# SPEECH-TO-TEXT SERVICE
# =============================================================================

class SpeechToTextService:
    """
    Service for converting speech audio to text.
    
    Supports:
    - Hugging Face Whisper API (cloud, free tier available)
    - OpenAI Whisper API (cloud)
    - Local Whisper model (offline)
    
    Usage:
        stt_service = SpeechToTextService()
        result = await stt_service.transcribe("path/to/audio.mp3")
        print(result.text)
    """
    
    # Hugging Face Whisper model endpoint
    HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-base"
    
    def __init__(self):
        """Initialize the STT service."""
        self.model = None
        self.model_size = settings.whisper_model_size
        self.use_api = settings.whisper_use_api
        self.provider = settings.stt_provider  # huggingface, whisper, local
        self._initialize()
    
    def _initialize(self):
        """Initialize the transcription model or API client."""
        debug_log(f"Initializing STT service with provider: {self.provider}")
        
        # Try Hugging Face API first (free tier)
        if self.provider == "huggingface" and settings.huggingface_api_key:
            self.hf_api_key = settings.huggingface_api_key
            debug_log("Hugging Face API initialized")
            logger.info("Hugging Face Whisper API initialized")
            return
        
        # Try OpenAI Whisper API
        if self.provider == "whisper" and self.use_api:
            try:
                import openai
                if settings.openai_api_key:
                    openai.api_key = settings.openai_api_key
                    self.client = openai
                    debug_log("OpenAI Whisper API initialized")
                    logger.info("Whisper API client initialized")
                    return
            except ImportError:
                logger.warning("OpenAI package not installed")
        
        # Fallback to local model
        debug_log("Falling back to local Whisper model")
        self._load_local_model()
    
    def _load_local_model(self):
        """Load local Whisper model."""
        try:
            import whisper
            debug_log(f"Loading local Whisper model: {self.model_size}")
            logger.info(f"Loading local Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.provider = "local"
            debug_log("Local Whisper model loaded successfully")
            logger.info("Local Whisper model loaded successfully")
        except ImportError:
            logger.error("Whisper package not installed. Install with: pip install openai-whisper")
            raise RuntimeError("Whisper not available. Install with: pip install openai-whisper")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        include_timestamps: bool = False
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
            include_timestamps: Whether to include word timestamps
        
        Returns:
            TranscriptionResult with transcribed text and metadata
        
        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        debug_log("=== TRANSCRIBE AUDIO ===")
        debug_log("Input params", {"audio_path": audio_path, "language": language})
        
        # Validate file exists
        if not os.path.exists(audio_path):
            debug_log("ERROR: File not found", audio_path)
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get file info
        file_size = os.path.getsize(audio_path)
        file_ext = Path(audio_path).suffix.lower()
        
        debug_log("File info", {"size": file_size, "ext": file_ext})
        logger.info(f"Transcribing: {audio_path} ({file_size} bytes, {file_ext})")
        
        # Validate file format
        supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        if file_ext not in supported_formats:
            debug_log("ERROR: Unsupported format", file_ext)
            raise ValueError(f"Unsupported audio format: {file_ext}")
        
        # Transcribe based on provider
        if self.provider == "huggingface" and hasattr(self, 'hf_api_key'):
            debug_log("Using Hugging Face API...")
            return await self._transcribe_huggingface(audio_path, language)
        elif self.provider == "whisper" and hasattr(self, 'client'):
            debug_log("Using OpenAI Whisper API...")
            return await self._transcribe_api(audio_path, language, include_timestamps)
        else:
            debug_log("Using local Whisper model...")
            return await self._transcribe_local(audio_path, language, include_timestamps)
    
    async def _transcribe_huggingface(
        self,
        audio_path: str,
        language: Optional[str],
        retry_count: int = 0
    ) -> TranscriptionResult:
        """Transcribe using Hugging Face Whisper API (free tier)."""
        MAX_RETRIES = 3
        debug_log("Calling Hugging Face API...")

        try:
            # Read audio file
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()

            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "audio/webm"  # or detect from file
            }

            # Use httpx for async HTTP requests
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.HF_API_URL,
                    headers=headers,
                    content=audio_data
                )

                if response.status_code == 200:
                    result = response.json()
                    text = result.get("text", "")
                    debug_log("Hugging Face transcription SUCCESS", {"text_length": len(text)})

                    return TranscriptionResult(
                        text=text.strip(),
                        language=language or "en",
                        duration=0.0,
                        confidence=0.9,
                        word_timestamps=None,
                        segments=None
                    )
                elif response.status_code == 503 and retry_count < MAX_RETRIES:
                    # Model is loading, wait and retry with limit
                    debug_log(f"Model loading, retrying in 20s... (attempt {retry_count + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(20)
                    return await self._transcribe_huggingface(audio_path, language, retry_count + 1)
                else:
                    error_msg = response.text
                    debug_log("Hugging Face API error", {"status": response.status_code, "error": error_msg})
                    raise RuntimeError(f"Hugging Face API error: {response.status_code} - {error_msg}")

        except Exception as e:
            debug_log("Hugging Face transcription FAILED", str(e))
            logger.error(f"Hugging Face transcription failed: {e}")
            # Fallback to local model
            if self.model:
                return await self._transcribe_local(audio_path, language, False)
            raise RuntimeError(f"Transcription failed: {e}")
    
    async def _transcribe_api(
        self,
        audio_path: str,
        language: Optional[str],
        include_timestamps: bool
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API."""
        
        loop = asyncio.get_event_loop()
        
        def _call_api():
            with open(audio_path, "rb") as audio_file:
                # Basic transcription
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json" if include_timestamps else "json"
                )
                return transcript
        
        try:
            result = await loop.run_in_executor(None, _call_api)
            
            # Parse response
            if hasattr(result, 'segments'):
                segments = [
                    {
                        'start': s.get('start', 0),
                        'end': s.get('end', 0),
                        'text': s.get('text', '')
                    }
                    for s in result.segments
                ]
            else:
                segments = None
            
            return TranscriptionResult(
                text=result.text,
                language=getattr(result, 'language', language or 'en'),
                duration=getattr(result, 'duration', 0.0),
                confidence=0.95,  # API doesn't return confidence
                word_timestamps=None,  # Not available in basic API
                segments=segments
            )
        
        except Exception as e:
            logger.error(f"API transcription failed: {e}")
            # Fallback to local if API fails
            if self.model:
                return await self._transcribe_local(audio_path, language, include_timestamps)
            raise RuntimeError(f"Transcription failed: {e}")
    
    async def _transcribe_local(
        self,
        audio_path: str,
        language: Optional[str],
        include_timestamps: bool
    ) -> TranscriptionResult:
        """Transcribe using local Whisper model."""
        
        if not self.model:
            self._load_local_model()
        
        loop = asyncio.get_event_loop()
        
        def _transcribe():
            options = {
                "language": language,
                "word_timestamps": include_timestamps,
                "fp16": False  # Use FP32 for better compatibility
            }
            return self.model.transcribe(audio_path, **options)
        
        try:
            result = await loop.run_in_executor(None, _transcribe)
            
            # Extract word timestamps if requested
            word_timestamps = None
            if include_timestamps and 'segments' in result:
                word_timestamps = []
                for segment in result['segments']:
                    if 'words' in segment:
                        word_timestamps.extend(segment['words'])
            
            # Calculate average confidence
            segments = result.get('segments', [])
            if segments:
                avg_confidence = sum(
                    s.get('no_speech_prob', 0) for s in segments
                ) / len(segments)
                confidence = 1.0 - avg_confidence  # Convert to confidence
            else:
                confidence = 0.0
            
            return TranscriptionResult(
                text=result.get('text', '').strip(),
                language=result.get('language', language or 'en'),
                duration=result.get('duration', 0.0),
                confidence=confidence,
                word_timestamps=word_timestamps,
                segments=[
                    {
                        'start': s.get('start', 0),
                        'end': s.get('end', 0),
                        'text': s.get('text', '').strip()
                    }
                    for s in segments
                ]
            )
        
        except Exception as e:
            logger.error(f"Local transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {e}")
    
    async def transcribe_chunk(
        self,
        audio_data: bytes,
        format: str = "wav"
    ) -> TranscriptionResult:
        """
        Transcribe audio from bytes (for streaming).
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, etc.)
        
        Returns:
            TranscriptionResult
        """
        import tempfile
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f".{format}",
            delete=False
        ) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            result = await self.transcribe(tmp_path)
            return result
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages."""
        return [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru',
            'zh', 'ja', 'ko', 'ar', 'hi', 'tr', 'vi', 'th', 'id'
        ]
    
    def is_available(self) -> bool:
        """Check if STT service is available."""
        return self.model is not None or (self.use_api and self.client is not None)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

_stt_service: Optional[SpeechToTextService] = None


def get_stt_service() -> SpeechToTextService:
    """Factory function to get STT service instance (singleton)."""
    global _stt_service
    if _stt_service is None:
        _stt_service = SpeechToTextService()
    return _stt_service
