"""
═══════════════════════════════════════════════════════════
RecruitAI — Job Models
═══════════════════════════════════════════════════════════
Pydantic schemas for job postings scraped from boards,
manual entry, and database document representation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class JobSource(str, Enum):
    """Source platform for the job posting."""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    WELLFOUND = "wellfound"
    COMPANY_SITE = "company_site"
    MANUAL = "manual"
    OTHER = "other"


class JobStatus(str, Enum):
    """Status of the job posting."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLOSED = "closed"


class JobType(str, Enum):
    """Employment type."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    HYBRID = "hybrid"


# ─── Request Schemas ──────────────────────────────────────

class JobCreateRequest(BaseModel):
    """Manual job entry request."""
    title: str = Field(..., min_length=2, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    url: Optional[str] = None
    location: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    skills_required: List[str] = []
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None


class JobSearchRequest(BaseModel):
    """Job search/filter request."""
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    source: Optional[JobSource] = None
    min_match_score: Optional[float] = Field(None, ge=0, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# ─── Response Schemas ─────────────────────────────────────

class JobResponse(BaseModel):
    """Job data returned in API responses."""
    id: str
    title: str
    company: str
    description: str
    url: Optional[str] = None
    location: Optional[str] = None
    job_type: str
    skills_required: List[str] = []
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    source: str
    status: str
    posted_at: Optional[datetime] = None
    created_at: datetime


class JobBriefResponse(BaseModel):
    """Brief job info for list views."""
    id: str
    title: str
    company: str
    location: Optional[str] = None
    job_type: str
    skills_required: List[str] = []
    source: str
    posted_at: Optional[datetime] = None


# ─── Database Document ────────────────────────────────────

class JobDocument(BaseModel):
    """Full job document as stored in MongoDB."""
    title: str
    company: str
    description: str
    url: Optional[str] = None
    location: Optional[str] = None
    job_type: str = JobType.FULL_TIME.value
    skills_required: List[str] = []
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    source: str = JobSource.MANUAL.value
    status: str = JobStatus.ACTIVE.value
    description_embedding: Optional[List[float]] = None
    posted_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self, doc_id: str) -> JobResponse:
        return JobResponse(
            id=doc_id,
            title=self.title,
            company=self.company,
            description=self.description,
            url=self.url,
            location=self.location,
            job_type=self.job_type,
            skills_required=self.skills_required,
            experience_required=self.experience_required,
            salary_range=self.salary_range,
            source=self.source,
            status=self.status,
            posted_at=self.posted_at,
            created_at=self.created_at,
        )

    def to_brief(self, doc_id: str) -> JobBriefResponse:
        return JobBriefResponse(
            id=doc_id,
            title=self.title,
            company=self.company,
            location=self.location,
            job_type=self.job_type,
            skills_required=self.skills_required,
            source=self.source,
            posted_at=self.posted_at,
        )
