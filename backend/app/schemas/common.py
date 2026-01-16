"""
==============================================================================
AI Mock Interview System - Common Schemas
==============================================================================

Common/shared Pydantic schemas used across the application.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

# Generic type for paginated responses
T = TypeVar("T")


# =============================================================================
# STANDARD API RESPONSES
# =============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "Resource not found",
                "error_code": "NOT_FOUND",
                "details": {"resource": "user", "id": "123"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    success: bool = False
    error: str = "Validation error"
    error_code: str = "VALIDATION_ERROR"
    details: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "details": [
                    {"field": "email", "message": "Invalid email format"},
                    {"field": "password", "message": "Password too short"}
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# PAGINATION
# =============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


# =============================================================================
# HEALTH CHECK
# =============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
    database_status: str = "connected"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: Optional[float] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "database_status": "connected",
                "timestamp": "2024-01-15T10:30:00Z",
                "uptime_seconds": 3600.5
            }
        }
    }


# =============================================================================
# FILE UPLOAD
# =============================================================================

class FileUploadResponse(BaseModel):
    """File upload response."""
    success: bool
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "filename": "recording.wav",
                "file_path": "/uploads/audio/recording_123.wav",
                "file_size": 1024000,
                "content_type": "audio/wav",
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }
    }


# =============================================================================
# SORTING & FILTERING
# =============================================================================

class SortParams(BaseModel):
    """Sorting parameters."""
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class DateRangeFilter(BaseModel):
    """Date range filter."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SearchParams(BaseModel):
    """Search parameters."""
    query: str = Field(..., min_length=1, max_length=200)
    fields: List[str] = Field(default_factory=list)
