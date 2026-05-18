"""
═══════════════════════════════════════════════════════════
RecruitAI — Common Response & Error Models
═══════════════════════════════════════════════════════════
Standardized API response schemas used across all endpoints.
"""

from typing import Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    success: bool = True
    message: str = "OK"
    data: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    app_name: str
    version: str
    environment: str
    mongodb: str = "unknown"
    redis: str = "unknown"
