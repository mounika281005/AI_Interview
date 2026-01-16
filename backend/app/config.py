"""
==============================================================================
AI Mock Interview System - Configuration Module
==============================================================================

This module handles all configuration settings using Pydantic Settings.
Settings are loaded from environment variables and .env file.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Usage:
        from app.config import get_settings
        settings = get_settings()
        print(settings.app_name)
    """
    
    # =========================================================================
    # APPLICATION SETTINGS
    # =========================================================================
    app_name: str = Field(default="AI Mock Interview System")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=True)
    environment: str = Field(default="development")
    
    # =========================================================================
    # SERVER SETTINGS
    # =========================================================================
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    
    # =========================================================================
    # DATABASE SETTINGS
    # =========================================================================
    database_url: str = Field(
        default="sqlite+aiosqlite:///./interview_system.db"
    )
    
    # =========================================================================
    # SECURITY SETTINGS
    # =========================================================================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-min-32-characters"
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    
    # =========================================================================
    # AI MODEL SETTINGS
    # =========================================================================
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    huggingface_api_key: Optional[str] = Field(default=None)
    huggingface_api_url: str = Field(default="https://router.huggingface.co/v1/chat/completions")
    huggingface_model: str = Field(default="meta-llama/Meta-Llama-3-8B-Instruct")
    ai_provider: str = Field(default="huggingface")  # openai, google, huggingface, local
    ai_model: str = Field(default="gpt-4-turbo-preview")
    
    # =========================================================================
    # SPEECH-TO-TEXT SETTINGS
    # =========================================================================
    stt_provider: str = Field(default="huggingface")  # whisper, huggingface, google, azure
    whisper_model: str = Field(default="base")  # tiny, base, small, medium, large
    whisper_model_size: str = Field(default="base")  # tiny, base, small, medium, large
    whisper_use_api: bool = Field(default=True)  # True=use API, False=local model
    google_cloud_credentials: Optional[str] = Field(default=None)
    
    # =========================================================================
    # FILE STORAGE SETTINGS
    # =========================================================================
    upload_dir: str = Field(default="./uploads")
    max_audio_size_mb: int = Field(default=50)
    allowed_audio_formats: str = Field(default="wav,mp3,m4a,webm,ogg")
    
    @property
    def allowed_audio_formats_list(self) -> List[str]:
        """Get allowed audio formats as a list."""
        return [fmt.strip() for fmt in self.allowed_audio_formats.split(",")]
    
    @property
    def max_audio_size_bytes(self) -> int:
        """Get max audio size in bytes."""
        return self.max_audio_size_mb * 1024 * 1024
    
    # =========================================================================
    # CORS SETTINGS
    # =========================================================================
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173"
    )
    cors_allow_credentials: bool = Field(default=True)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # =========================================================================
    # LOGGING SETTINGS
    # =========================================================================
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # =========================================================================
    # MODEL CONFIG
    # =========================================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # =========================================================================
    # VALIDATORS
    # =========================================================================
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production", "testing"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    def get_database_url(self, async_mode: bool = True) -> str:
        """
        Get database URL for sync or async mode.
        
        Args:
            async_mode: If True, return async-compatible URL
        
        Returns:
            Database URL string
        """
        if async_mode:
            return self.database_url
        # Convert async URL to sync if needed
        return self.database_url.replace("+aiosqlite", "").replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are only loaded once.
    
    Returns:
        Settings instance
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
