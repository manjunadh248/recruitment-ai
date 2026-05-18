"""
═══════════════════════════════════════════════════════════
RecruitAI — User Models
═══════════════════════════════════════════════════════════
Pydantic schemas for user registration, login, profile,
and database document representation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId serialization."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


# ─── Request Schemas ──────────────────────────────────────

class UserRegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=100)

    model_config = {"json_schema_extra": {
        "example": {
            "email": "john@example.com",
            "password": "securePass123!",
            "name": "John Doe"
        }
    }}


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """User profile update request."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=200)
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)


# ─── Response Schemas ─────────────────────────────────────

class UserResponse(BaseModel):
    """User data returned in API responses (no password)."""
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: List[str] = []
    experience_years: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AuthTokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Database Document ────────────────────────────────────

class UserDocument(BaseModel):
    """Full user document as stored in MongoDB."""
    email: str
    name: str
    password_hash: str
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: List[str] = []
    experience_years: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def to_response(self, doc_id: str) -> UserResponse:
        """Convert to API response (strips password)."""
        return UserResponse(
            id=doc_id,
            email=self.email,
            name=self.name,
            phone=self.phone,
            location=self.location,
            headline=self.headline,
            linkedin_url=self.linkedin_url,
            github_url=self.github_url,
            portfolio_url=self.portfolio_url,
            target_roles=self.target_roles,
            experience_years=self.experience_years,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
