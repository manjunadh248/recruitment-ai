"""
═══════════════════════════════════════════════════════════
RecruitAI — Resume Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.resume import ResumeDocument, ResumeUploadResponse, ResumeListItem


class ResumeRepository(BaseRepository):
    collection_name = "resumes"

    async def create_resume(self, doc: ResumeDocument) -> str:
        """Store a parsed resume."""
        return await self.insert_one(doc.model_dump())

    async def get_user_resumes(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all resumes for a user, most recent first."""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def get_primary_resume(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the user's primary resume."""
        return await self.find_one({"user_id": user_id, "is_primary": True})

    async def set_primary(self, user_id: str, resume_id: str) -> bool:
        """Set a resume as primary (unset others)."""
        # Unset all primary flags for this user
        await self.collection.update_many(
            {"user_id": user_id}, {"$set": {"is_primary": False}}
        )
        # Set the target as primary
        return await self.update_by_id(resume_id, {"$set": {"is_primary": True}})

    async def get_resume_with_text(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get resume with full raw text (for AI processing)."""
        return await self.find_by_id(resume_id)

    async def update_parsed_data(self, resume_id: str, parsed_data: dict, raw_text: str) -> bool:
        """Update the parsed data and raw text after processing."""
        return await self.update_by_id(resume_id, {
            "$set": {
                "parsed_data": parsed_data,
                "raw_text": raw_text,
            }
        })

    async def update_embeddings(self, resume_id: str, embeddings: list) -> bool:
        """Store skill embeddings for the resume."""
        return await self.update_by_id(resume_id, {
            "$set": {"skill_embeddings": embeddings}
        })


# Singleton instance
resume_repo = ResumeRepository()
