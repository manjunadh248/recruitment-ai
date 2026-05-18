"""
═══════════════════════════════════════════════════════════
RecruitAI — ATS Score Models
═══════════════════════════════════════════════════════════
Pydantic schemas for ATS compatibility scoring between
resumes and job descriptions.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


# ─── Sub-Models ───────────────────────────────────────────

class KeywordAnalysis(BaseModel):
    """Detailed keyword matching analysis."""
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    partial_matches: List[Dict[str, str]] = []  # {"resume": "...", "job": "..."}
    keyword_match_ratio: float = 0.0


class SectionScore(BaseModel):
    """Score breakdown by resume section."""
    summary: float = 0.0
    skills: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    projects: float = 0.0
    certifications: float = 0.0


class ATSSuggestion(BaseModel):
    """Single improvement suggestion."""
    category: str  # "keyword", "section", "formatting", "content"
    priority: str  # "high", "medium", "low"
    message: str
    action: Optional[str] = None  # Specific action to take


# ─── Request Schemas ──────────────────────────────────────

class ATSScoreRequest(BaseModel):
    """Request to score a resume against a job."""
    resume_id: str
    job_id: Optional[str] = None
    job_description: Optional[str] = None  # Alternative: paste JD directly
    job_title: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "resume_id": "6651a...",
            "job_id": "6651b...",
        }
    }}


# ─── Response Schemas ─────────────────────────────────────

class ATSScoreResponse(BaseModel):
    """ATS scoring result returned to the user."""
    id: str
    resume_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    overall_score: float = Field(..., ge=0, le=100)
    semantic_score: float = Field(..., ge=0, le=100)
    keyword_score: float = Field(..., ge=0, le=100)
    section_score: float = Field(..., ge=0, le=100)
    experience_score: float = Field(..., ge=0, le=100)
    education_score: float = Field(..., ge=0, le=100)
    grade: str  # "A+", "A", "B", "C", "D", "F"
    keyword_analysis: KeywordAnalysis
    section_scores: SectionScore
    suggestions: List[ATSSuggestion] = []
    created_at: datetime


# ─── Database Document ────────────────────────────────────

class ATSScoreDocument(BaseModel):
    """Full ATS score document as stored in MongoDB."""
    user_id: str
    resume_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    job_description_snippet: Optional[str] = None  # First 500 chars
    overall_score: float = 0.0
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    section_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    grade: str = "F"
    keyword_analysis: KeywordAnalysis = Field(default_factory=KeywordAnalysis)
    section_scores: SectionScore = Field(default_factory=SectionScore)
    suggestions: List[ATSSuggestion] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def calculate_grade(score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        return "F"

    def to_response(self, doc_id: str) -> ATSScoreResponse:
        return ATSScoreResponse(
            id=doc_id,
            resume_id=self.resume_id,
            job_id=self.job_id,
            job_title=self.job_title,
            overall_score=self.overall_score,
            semantic_score=self.semantic_score,
            keyword_score=self.keyword_score,
            section_score=self.section_score,
            experience_score=self.experience_score,
            education_score=self.education_score,
            grade=self.grade,
            keyword_analysis=self.keyword_analysis,
            section_scores=self.section_scores,
            suggestions=self.suggestions,
            created_at=self.created_at,
        )
