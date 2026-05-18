"""
═══════════════════════════════════════════════════════════
RecruitAI — Resume Models
═══════════════════════════════════════════════════════════
Pydantic schemas for resume upload, parsed data structure,
and database document representation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ─── Parsed Data Sub-Models ───────────────────────────────

class Education(BaseModel):
    """Single education entry extracted from resume."""
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None


class Experience(BaseModel):
    """Single work experience entry extracted from resume."""
    company: str = ""
    title: str = ""
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    highlights: List[str] = []


class Project(BaseModel):
    """Single project entry extracted from resume."""
    name: str = ""
    description: Optional[str] = None
    technologies: List[str] = []
    url: Optional[str] = None
    highlights: List[str] = []


class Certification(BaseModel):
    """Single certification entry."""
    name: str = ""
    issuer: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None


class ContactInfo(BaseModel):
    """Contact information extracted from resume."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    location: Optional[str] = None


class ParsedResumeData(BaseModel):
    """Structured data extracted from a resume by the AI parser."""
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[str] = []
    education: List[Education] = []
    experience: List[Experience] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    languages: List[str] = []
    total_experience_years: Optional[float] = None


# ─── Request Schemas ──────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    """Response after uploading and parsing a resume."""
    id: str
    user_id: str
    filename: str
    file_type: str
    parsed_data: ParsedResumeData
    skills_count: int
    is_primary: bool
    created_at: datetime


class ResumeListItem(BaseModel):
    """Brief resume info for list views."""
    id: str
    filename: str
    file_type: str
    skills_count: int
    is_primary: bool
    created_at: datetime


# ─── Database Document ────────────────────────────────────

class ResumeDocument(BaseModel):
    """Full resume document as stored in MongoDB."""
    user_id: str
    filename: str
    file_type: str  # "pdf" or "docx"
    file_path: str
    raw_text: str = ""
    parsed_data: ParsedResumeData = Field(default_factory=ParsedResumeData)
    skill_embeddings: Optional[List[List[float]]] = None
    is_primary: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def to_response(self, doc_id: str) -> ResumeUploadResponse:
        """Convert to API response."""
        return ResumeUploadResponse(
            id=doc_id,
            user_id=self.user_id,
            filename=self.filename,
            file_type=self.file_type,
            parsed_data=self.parsed_data,
            skills_count=len(self.parsed_data.skills),
            is_primary=self.is_primary,
            created_at=self.created_at,
        )

    def to_list_item(self, doc_id: str) -> ResumeListItem:
        """Convert to brief list item."""
        return ResumeListItem(
            id=doc_id,
            filename=self.filename,
            file_type=self.file_type,
            skills_count=len(self.parsed_data.skills),
            is_primary=self.is_primary,
            created_at=self.created_at,
        )
