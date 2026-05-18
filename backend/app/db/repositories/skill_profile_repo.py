"""
═══════════════════════════════════════════════════════════
RecruitAI — Skill Profile Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.skill_profile import SkillProfileDocument, SkillEntry
from datetime import datetime


class SkillProfileRepository(BaseRepository):
    collection_name = "skill_profiles"

    async def get_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the skill profile for a user."""
        return await self.find_one({"user_id": user_id})

    async def upsert_profile(self, doc: SkillProfileDocument) -> str:
        """Create or update the skill profile for a user."""
        return await self.upsert_one(
            {"user_id": doc.user_id},
            {"$set": doc.model_dump()},
        )

    async def add_skills(self, user_id: str, skills: List[Dict[str, Any]]) -> bool:
        """Add new skills to an existing profile (no duplicates)."""
        existing = await self.get_by_user(user_id)
        if not existing:
            return False

        existing_names = {s["name"].lower() for s in existing.get("skills", [])}
        new_skills = [s for s in skills if s["name"].lower() not in existing_names]

        if not new_skills:
            return False

        return await self.update_one(
            {"user_id": user_id},
            {
                "$push": {"skills": {"$each": new_skills}},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

    async def update_embeddings(self, user_id: str, embeddings: List[List[float]]) -> bool:
        """Update the skill embeddings vector."""
        return await self.update_one(
            {"user_id": user_id},
            {"$set": {
                "skill_embeddings": embeddings,
                "updated_at": datetime.utcnow(),
            }},
        )

    async def get_user_skills_list(self, user_id: str) -> List[str]:
        """Get just the skill names for a user."""
        doc = await self.get_by_user(user_id)
        if not doc:
            return []
        return [s.get("name", "") for s in doc.get("skills", [])]


# Singleton instance
skill_profile_repo = SkillProfileRepository()
