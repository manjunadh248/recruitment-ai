"""
═══════════════════════════════════════════════════════════
RecruitAI — Skill Profile Models
═══════════════════════════════════════════════════════════
Pydantic schemas for the aggregated skill profile per user,
including proficiency levels and semantic embeddings.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SkillEntry(BaseModel):
    """Single skill with metadata."""
    name: str
    category: str = "general"  # "language", "framework", "tool", "soft_skill", "domain"
    proficiency: str = "intermediate"  # "beginner", "intermediate", "advanced", "expert"
    years_used: Optional[float] = None
    last_used: Optional[str] = None
    source: str = "resume"  # "resume", "manual", "inferred"


class SkillProfileResponse(BaseModel):
    """Skill profile returned to the user."""
    id: str
    user_id: str
    skills: List[SkillEntry] = []
    top_skills: List[str] = []
    skill_categories: Dict[str, List[str]] = {}
    total_skills: int = 0
    last_updated: datetime


class SkillProfileDocument(BaseModel):
    """Full skill profile document as stored in MongoDB."""
    user_id: str
    skills: List[SkillEntry] = []
    top_skills: List[str] = []
    skill_categories: Dict[str, List[str]] = {}
    skill_embeddings: Optional[List[List[float]]] = None  # SBERT vectors
    embedding_model: str = "all-MiniLM-L6-v2"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self, doc_id: str) -> SkillProfileResponse:
        return SkillProfileResponse(
            id=doc_id,
            user_id=self.user_id,
            skills=self.skills,
            top_skills=self.top_skills,
            skill_categories=self.skill_categories,
            total_skills=len(self.skills),
            last_updated=self.updated_at,
        )
