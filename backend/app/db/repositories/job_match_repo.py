"""
═══════════════════════════════════════════════════════════
RecruitAI — Job Match Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.job_match import JobMatchDocument


class JobMatchRepository(BaseRepository):
    collection_name = "job_matches"

    async def create_match(self, doc: JobMatchDocument) -> str:
        """Store a new job match result."""
        return await self.insert_one(doc.model_dump())

    async def bulk_create_matches(self, docs: List[JobMatchDocument]) -> List[str]:
        """Bulk insert match results from a matching run."""
        return await self.insert_many([d.model_dump() for d in docs])

    async def get_user_matches(
        self,
        user_id: str,
        min_score: float = 0.0,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get ranked job matches for a user above a minimum score."""
        query: Dict[str, Any] = {
            "user_id": user_id,
            "match_score": {"$gte": min_score},
            "is_dismissed": False,
        }
        return await self.find_many(
            query,
            sort=[("match_score", -1)],
            skip=skip,
            limit=limit,
        )

    async def get_top_matches(self, user_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top N matches for a user."""
        return await self.get_user_matches(user_id, limit=top_n)

    async def dismiss_match(self, match_id: str) -> bool:
        """Dismiss a job match (user not interested)."""
        return await self.update_by_id(match_id, {"$set": {"is_dismissed": True}})

    async def upsert_match(self, user_id: str, job_id: str, doc: JobMatchDocument) -> str:
        """Upsert a match for a user-job pair."""
        return await self.upsert_one(
            {"user_id": user_id, "job_id": job_id},
            {"$set": doc.model_dump()},
        )

    async def clear_user_matches(self, user_id: str) -> int:
        """Clear all matches for a user (before re-matching)."""
        return await self.delete_many({"user_id": user_id})

    async def get_match_stats(self, user_id: str) -> Dict[str, Any]:
        """Get match statistics for a user."""
        pipeline = [
            {"$match": {"user_id": user_id, "is_dismissed": False}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "avg_score": {"$avg": "$match_score"},
                "max_score": {"$max": "$match_score"},
                "min_score": {"$min": "$match_score"},
            }},
        ]
        results = await self.aggregate(pipeline)
        if results:
            return results[0]
        return {"total": 0, "avg_score": 0, "max_score": 0, "min_score": 0}


# Singleton instance
job_match_repo = JobMatchRepository()
