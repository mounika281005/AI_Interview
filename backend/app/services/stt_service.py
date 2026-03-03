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
import re
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
# WHISPER HALLUCINATION DETECTION
# =============================================================================

# Known Whisper hallucination patterns (produced on silent/near-silent audio)
WHISPER_HALLUCINATION_PATTERNS = [
    r"^thank(s| you)( for)? (watching|listening|viewing)",
    r"^subtitles? (by|from)",
    r"^(please )?(subscribe|like|comment)",
    r"^(this is|this was) (a )?recording",
    r"^you$",
    r"^\.$",
    r"^bye[\.\!]?$",
    r"^(the end|end)[\.\!]?$",
    r"^okay[\.\!]?$",
    r"^(um|uh|hmm|ah)[\.\!]?$",
    r"^silence[\.\!]?$",
    r"^amara\.org",
    r"^www\.",
    r"^http",
    r"^copyright",
    r"^music[\.\!]?$",
    r"^\[.*\]$",  # Bracketed text like [Music], [Silence], etc.
    r"^MorusMedia",
    r"^Transcriber:",
    r"^Reviewed by",
    # Additional patterns for longer hallucinations
    r"^in this video",
    r"^welcome to",
    r"^hello everyone",
    r"^hi (guys|everyone|there)",
    r"^(the |this )?(video|episode|chapter|session)",
    r"^(please |don'?t )?(forget to )?(subscribe|like|share|comment)",
    r"^(i'?m|we'?re) (going to|gonna)",
    r"^let'?s (get started|begin|go)",
    r"^so (today|in this)",
    r"^(and |so |but )?(that'?s|this is) (it|all)",
]

# Minimum confidence threshold — below this we treat the transcript as unreliable
MIN_CONFIDENCE_THRESHOLD = 0.15

# Minimum word count for a valid transcript
MIN_TRANSCRIPT_WORDS = 3


def is_hallucination(text: str) -> bool:
    """Check if a transcript is a known Whisper hallucination."""
    if not text or not text.strip():
        return True

    cleaned = text.strip()

    # Check against known hallucination patterns (case-insensitive)
    for pattern in WHISPER_HALLUCINATION_PATTERNS:
        if re.match(pattern, cleaned, re.IGNORECASE):
            debug_log("Hallucination detected", {"text": cleaned, "pattern": pattern})
            return True

    # Extremely short text is likely not a real answer
    word_count = len(cleaned.split())
    if word_count < MIN_TRANSCRIPT_WORDS:
        debug_log("Transcript too short", {"word_count": word_count, "text": cleaned})
        return True

    # Detect repetitive text (common Whisper hallucination on silence)
    words = cleaned.lower().split()
    if len(words) >= 6:
        # Check if the same short phrase repeats
        for phrase_len in range(2, min(6, len(words) // 2 + 1)):
            phrase = " ".join(words[:phrase_len])
            repeat_count = 0
            for i in range(0, len(words) - phrase_len + 1, phrase_len):
                if " ".join(words[i:i + phrase_len]) == phrase:
                    repeat_count += 1
            if repeat_count >= 3:
                debug_log("Repetitive hallucination detected",
                          {"phrase": phrase, "repeats": repeat_count})
                return True

    return False


def sanitize_transcript(result: 'TranscriptionResult') -> 'TranscriptionResult':
    """
    Validate and sanitize a transcription result.

    Returns the result with text cleared if the transcript is a hallucination
    or below confidence threshold.
    """
    text = result.text.strip() if result.text else ""

    # Check confidence threshold
    if result.confidence < MIN_CONFIDENCE_THRESHOLD and text:
        debug_log("Low confidence transcript rejected",
                  {"confidence": result.confidence, "text": text[:100]})
        result.text = ""
        result.confidence = 0.0
        return result

    # Check for hallucination
    if is_hallucination(text):
        debug_log("Hallucinated transcript cleared",
                  {"original_text": text[:100], "confidence": result.confidence})
        result.text = ""
        result.confidence = 0.0
        return result

    return result


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
    
    # Hugging Face Whisper model endpoint (updated — old api-inference URL is 410 Gone)
    HF_API_URL = "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3"
    
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
            logger.warning("Whisper package not installed. Using mock transcription fallback.")
            logger.info("To enable real transcription, install with: pip install openai-whisper")
            self.provider = "mock"
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            logger.warning("Using mock transcription fallback")
            self.provider = "mock"
            self.model = None
    
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
            result = await self._transcribe_huggingface(audio_path, language)
        elif self.provider == "whisper" and hasattr(self, 'client'):
            debug_log("Using OpenAI Whisper API...")
            result = await self._transcribe_api(audio_path, language, include_timestamps)
        elif self.provider == "local" and self.model:
            debug_log("Using local Whisper model...")
            result = await self._transcribe_local(audio_path, language, include_timestamps)
        else:
            debug_log("No STT provider available — returning empty transcript")
            logger.warning("No STT provider configured. Returning empty transcript.")
            result = await self._transcribe_mock(audio_path, language)

        # Post-process: filter hallucinations and low-confidence transcripts
        result = sanitize_transcript(result)
        debug_log("Final transcript after sanitization",
                  {"text_length": len(result.text), "confidence": result.confidence,
                   "preview": result.text[:100] if result.text else "(empty)"})
        return result
    
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

            # Detect content type from file extension
            ext = Path(audio_path).suffix.lower()
            content_types = {
                '.webm': 'audio/webm', '.wav': 'audio/wav', '.mp3': 'audio/mpeg',
                '.m4a': 'audio/mp4', '.ogg': 'audio/ogg', '.flac': 'audio/flac',
            }
            content_type = content_types.get(ext, 'audio/wav')

            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": content_type,
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
                    text = result.get("text", "").strip()
                    debug_log("Hugging Face transcription SUCCESS", {"text_length": len(text)})

                    # Estimate confidence based on text quality
                    # HuggingFace API doesn't return confidence, so we estimate:
                    # - Empty or very short text likely means silence/noise
                    # - Known hallucination patterns get low confidence
                    word_count = len(text.split()) if text else 0
                    if not text or word_count == 0:
                        estimated_confidence = 0.0
                    elif word_count < MIN_TRANSCRIPT_WORDS:
                        estimated_confidence = 0.1
                    elif is_hallucination(text):
                        estimated_confidence = 0.05
                    else:
                        estimated_confidence = 0.85

                    return TranscriptionResult(
                        text=text,
                        language=language or "en",
                        duration=0.0,
                        confidence=estimated_confidence,
                        word_timestamps=None,
                        segments=None
                    )
                elif response.status_code == 401:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_data.get("error", response.text[:200])
                    logger.error(f"HuggingFace API auth failed: {error_msg}")
                    raise RuntimeError(f"HuggingFace API key is invalid or expired. Please update HUGGINGFACE_API_KEY in .env")
                elif response.status_code == 503 and retry_count < MAX_RETRIES:
                    # Model is loading, wait and retry with limit
                    debug_log(f"Model loading, retrying in 20s... (attempt {retry_count + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(20)
                    return await self._transcribe_huggingface(audio_path, language, retry_count + 1)
                else:
                    error_msg = response.text[:200]
                    debug_log("Hugging Face API error", {"status": response.status_code, "error": error_msg})
                    raise RuntimeError(f"Hugging Face API error: {response.status_code} - {error_msg}")

        except Exception as e:
            debug_log("Hugging Face transcription FAILED", str(e))
            logger.error(f"Hugging Face transcription failed: {e}")
            # Fallback to local model if available, otherwise propagate error
            if self.model:
                try:
                    return await self._transcribe_local(audio_path, language, False)
                except Exception as local_err:
                    logger.error(f"Local fallback also failed: {local_err}")
            raise RuntimeError(f"Hugging Face transcription failed: {e}")
    
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
            
            # Estimate confidence — API doesn't return it directly
            text = result.text.strip() if result.text else ""
            word_count = len(text.split()) if text else 0
            if not text or word_count == 0:
                estimated_confidence = 0.0
            elif word_count < MIN_TRANSCRIPT_WORDS:
                estimated_confidence = 0.1
            elif is_hallucination(text):
                estimated_confidence = 0.05
            else:
                estimated_confidence = 0.9

            return TranscriptionResult(
                text=text,
                language=getattr(result, 'language', language or 'en'),
                duration=getattr(result, 'duration', 0.0),
                confidence=estimated_confidence,
                word_timestamps=None,  # Not available in basic API
                segments=segments
            )
        
        except Exception as e:
            logger.error(f"API transcription failed: {e}")
            # Fallback to local model if available, otherwise propagate error
            if self.model:
                try:
                    return await self._transcribe_local(audio_path, language, include_timestamps)
                except Exception as local_err:
                    logger.error(f"Local fallback also failed: {local_err}")
            raise RuntimeError(f"OpenAI Whisper transcription failed: {e}")
    
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

    async def _transcribe_mock(
        self,
        audio_path: str,
        language: Optional[str]
    ) -> TranscriptionResult:
        """
        Mock transcription when no STT service is available.

        Returns empty text so that the evaluation pipeline correctly
        detects "no speech" and assigns a score of 0.  Previous versions
        returned fabricated answers which polluted scoring.
        """
        debug_log("Using MOCK transcription (no real STT available)")
        logger.warning("No STT provider configured — returning empty transcript. "
                       "Install Whisper or set HUGGINGFACE_API_KEY for real transcription.")

        # Get audio duration for metadata only
        duration_seconds = 0.0
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            duration_seconds = len(audio) / 1000.0
        except Exception:
            file_size = os.path.getsize(audio_path)
            duration_seconds = file_size / 16000  # Rough estimate

        debug_log(f"Audio duration: {duration_seconds}s (mock — no transcript produced)")

        return TranscriptionResult(
            text="",
            language=language or "en",
            duration=duration_seconds,
            confidence=0.0,
            word_timestamps=None,
            segments=None
        )

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
