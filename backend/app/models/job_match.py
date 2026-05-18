"""
═══════════════════════════════════════════════════════════
RecruitAI — Job Match Models
═══════════════════════════════════════════════════════════
Pydantic schemas for AI-computed job-candidate matches
with skill overlap and ranking data.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SkillOverlap(BaseModel):
    """Detailed skill matching between candidate and job."""
    matched: List[str] = []
    missing: List[str] = []
    extra: List[str] = []  # Candidate skills not in JD
    match_ratio: float = 0.0


class JobMatchResponse(BaseModel):
    """Job match result returned to the user."""
    id: str
    user_id: str
    job_id: str
    job_title: str
    company: str
    location: Optional[str] = None
    match_score: float = Field(..., ge=0, le=1)
    skill_overlap: SkillOverlap
    experience_match: float = 0.0
    semantic_similarity: float = 0.0
    ranking: int = 0
    match_reasons: List[str] = []
    created_at: datetime


class JobMatchDocument(BaseModel):
    """Full job match document as stored in MongoDB."""
    user_id: str
    job_id: str
    match_score: float = 0.0
    skill_overlap: SkillOverlap = Field(default_factory=SkillOverlap)
    experience_match: float = 0.0
    location_match: float = 0.0
    semantic_similarity: float = 0.0
    company_tier_score: float = 0.0
    recency_boost: float = 0.0
    ranking: int = 0
    match_reasons: List[str] = []
    is_dismissed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self, doc_id: str, job_title: str = "", company: str = "", location: str = None) -> JobMatchResponse:
        return JobMatchResponse(
            id=doc_id,
            user_id=self.user_id,
            job_id=self.job_id,
            job_title=job_title,
            company=company,
            location=location,
            match_score=self.match_score,
            skill_overlap=self.skill_overlap,
            experience_match=self.experience_match,
            semantic_similarity=self.semantic_similarity,
            ranking=self.ranking,
            match_reasons=self.match_reasons,
            created_at=self.created_at,
        )
