"""
═══════════════════════════════════════════════════════════
RecruitAI — Optimized Resume Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.optimized_resume import OptimizedResumeDocument


class OptimizedResumeRepository(BaseRepository):
    collection_name = "optimized_resumes"

    async def create_version(self, doc: OptimizedResumeDocument) -> str:
        """Store a new personalized resume version."""
        return await self.insert_one(doc.model_dump())

    async def get_versions_for_job(
        self, user_id: str, job_id: str
    ) -> List[Dict[str, Any]]:
        """Get all personalized versions for a user-job pair."""
        return await self.find_many(
            {"user_id": user_id, "job_id": job_id},
            sort=[("version", -1)],
        )

    async def get_latest_version_number(self, user_id: str, job_id: str) -> int:
        """Get the latest version number for a user-job pair."""
        doc = await self.find_one({
            "user_id": user_id,
            "job_id": job_id,
        })
        if not doc:
            return 0
        # Get max version via sort
        docs = await self.find_many(
            {"user_id": user_id, "job_id": job_id},
            sort=[("version", -1)],
            limit=1,
        )
        return docs[0]["version"] if docs else 0

    async def get_user_optimized_resumes(
        self, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all optimized resumes for a user."""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def update_pdf_path(self, doc_id: str, pdf_path: str) -> bool:
        """Update the generated PDF path."""
        return await self.update_by_id(doc_id, {"$set": {"pdf_path": pdf_path}})

    async def update_ats_scores(
        self, doc_id: str, before: float, after: float
    ) -> bool:
        """Update ATS scores and improvement delta."""
        return await self.update_by_id(doc_id, {
            "$set": {
                "ats_score_before": before,
                "ats_score_after": after,
                "ats_improvement": round(after - before, 2),
            }
        })


# Singleton instance
optimized_resume_repo = OptimizedResumeRepository()
