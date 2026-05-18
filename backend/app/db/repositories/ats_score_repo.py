"""
═══════════════════════════════════════════════════════════
RecruitAI — ATS Score Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.ats_score import ATSScoreDocument


class ATSScoreRepository(BaseRepository):
    collection_name = "ats_scores"

    async def create_score(self, doc: ATSScoreDocument) -> str:
        """Store a new ATS score result."""
        return await self.insert_one(doc.model_dump())

    async def find_by_resume_and_job(self, resume_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Find existing score for a resume-job pair."""
        return await self.find_one({"resume_id": resume_id, "job_id": job_id})

    async def upsert_score(self, resume_id: str, job_id: str, doc: ATSScoreDocument) -> str:
        """Upsert ATS score for a resume-job pair."""
        return await self.upsert_one(
            {"resume_id": resume_id, "job_id": job_id},
            {"$set": doc.model_dump()}
        )

    async def get_user_scores(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all ATS scores for a user, highest first."""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("overall_score", -1)],
            limit=limit,
        )

    async def get_user_average_score(self, user_id: str) -> float:
        """Calculate average ATS score for a user."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "avg_score": {"$avg": "$overall_score"}}},
        ]
        results = await self.aggregate(pipeline)
        return results[0]["avg_score"] if results else 0.0

    async def get_score_distribution(self, user_id: str) -> Dict[str, int]:
        """Get grade distribution for a user's scores."""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$grade", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        results = await self.aggregate(pipeline)
        return {r["_id"]: r["count"] for r in results}


# Singleton instance
ats_score_repo = ATSScoreRepository()
