"""
═══════════════════════════════════════════════════════════
RecruitAI — Job Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.job import JobDocument


class JobRepository(BaseRepository):
    collection_name = "jobs"

    async def create_job(self, doc: JobDocument) -> str:
        """Store a new job posting."""
        return await self.insert_one(doc.model_dump())

    async def bulk_create_jobs(self, docs: List[JobDocument]) -> List[str]:
        """Bulk insert scraped jobs."""
        return await self.insert_many([d.model_dump() for d in docs])

    async def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        source: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search and filter jobs."""
        filter_query: Dict[str, Any] = {"status": "active"}

        if query:
            filter_query["$text"] = {"$search": query}
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
        if job_type:
            filter_query["job_type"] = job_type
        if source:
            filter_query["source"] = source

        sort = [("created_at", -1)]
        if query:
            sort = [("score", {"$meta": "textScore"})] + sort

        return await self.find_many(filter_query, sort=sort, skip=skip, limit=limit)

    async def get_active_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active jobs for matching pipeline."""
        return await self.find_many(
            {"status": "active"},
            sort=[("created_at", -1)],
            limit=limit,
        )

    async def get_jobs_without_embeddings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs that need embedding computation."""
        return await self.find_many(
            {"status": "active", "description_embedding": None},
            limit=limit,
        )

    async def update_embedding(self, job_id: str, embedding: List[float]) -> bool:
        """Store the computed description embedding."""
        return await self.update_by_id(job_id, {
            "$set": {"description_embedding": embedding}
        })

    async def mark_expired(self, job_id: str) -> bool:
        """Mark a job as expired."""
        return await self.update_by_id(job_id, {"$set": {"status": "expired"}})

    async def job_url_exists(self, url: str) -> bool:
        """Check if a job URL already exists (dedup for scraping)."""
        return await self.exists({"url": url})


# Singleton instance
job_repo = JobRepository()
