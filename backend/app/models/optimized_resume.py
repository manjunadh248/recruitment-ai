"""
═══════════════════════════════════════════════════════════
RecruitAI — Optimized Resume Models
═══════════════════════════════════════════════════════════
Pydantic schemas for job-tailored personalized resumes
with version tracking and ATS improvement metrics.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PersonalizedContent(BaseModel):
    """The AI-personalized resume content."""
    summary: str = ""
    skills: List[str] = []
    experience_highlights: List[str] = []
    project_highlights: List[str] = []
    keywords_injected: List[str] = []
    full_text: str = ""


class PersonalizeRequest(BaseModel):
    """Request to generate a personalized resume."""
    resume_id: str
    job_id: Optional[str] = None
    job_description: Optional[str] = None
    job_title: Optional[str] = None
    optimization_level: str = Field("balanced", pattern="^(conservative|balanced|aggressive)$")


class OptimizedResumeResponse(BaseModel):
    """Personalized resume response."""
    id: str
    user_id: str
    resume_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    version: int
    personalized_content: PersonalizedContent
    ats_score_before: Optional[float] = None
    ats_score_after: Optional[float] = None
    ats_improvement: Optional[float] = None
    pdf_path: Optional[str] = None
    created_at: datetime


class OptimizedResumeDocument(BaseModel):
    """Full optimized resume document as stored in MongoDB."""
    user_id: str
    resume_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    version: int = 1
    optimization_level: str = "balanced"
    personalized_content: PersonalizedContent = Field(default_factory=PersonalizedContent)
    ats_score_before: Optional[float] = None
    ats_score_after: Optional[float] = None
    ats_improvement: Optional[float] = None
    pdf_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self, doc_id: str) -> OptimizedResumeResponse:
        return OptimizedResumeResponse(
            id=doc_id,
            user_id=self.user_id,
            resume_id=self.resume_id,
            job_id=self.job_id,
            job_title=self.job_title,
            version=self.version,
            personalized_content=self.personalized_content,
            ats_score_before=self.ats_score_before,
            ats_score_after=self.ats_score_after,
            ats_improvement=self.ats_improvement,
            pdf_path=self.pdf_path,
            created_at=self.created_at,
        )
