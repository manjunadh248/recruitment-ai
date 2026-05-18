"""
═══════════════════════════════════════════════════════════
RecruitAI — Base Repository
═══════════════════════════════════════════════════════════
Generic async MongoDB repository with CRUD operations.
All collection-specific repositories inherit from this.
"""

from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from app.db.connection import MongoDB

T = TypeVar("T")


class BaseRepository:
    """
    Base MongoDB repository providing reusable CRUD operations.
    Subclasses set `collection_name` to target a specific collection.
    """

    collection_name: str = ""

    @property
    def collection(self):
        """Get the MongoDB collection for this repository."""
        return MongoDB.get_collection(self.collection_name)

    # ─── Create ───────────────────────────────────────────

    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert a single document. Returns the inserted ID as string."""
        result = await self.collection.insert_one(document)
        logger.debug(f"Inserted into {self.collection_name}: {result.inserted_id}")
        return str(result.inserted_id)

    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents. Returns list of inserted IDs."""
        result = await self.collection.insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]

    # ─── Read ─────────────────────────────────────────────

    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find a single document by its ObjectId."""
        if not ObjectId.is_valid(doc_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document by arbitrary query."""
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_many(
        self,
        query: Dict[str, Any],
        sort: Optional[List[tuple]] = None,
        skip: int = 0,
        limit: int = 50,
        projection: Optional[Dict[str, int]] = None,
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with optional sort, pagination, and projection."""
        cursor = self.collection.find(query, projection)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)

        docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            docs.append(doc)
        return docs

    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching the query."""
        return await self.collection.count_documents(query or {})

    # ─── Update ───────────────────────────────────────────

    async def update_by_id(self, doc_id: str, update: Dict[str, Any]) -> bool:
        """Update a document by ID. Returns True if modified."""
        if not ObjectId.is_valid(doc_id):
            return False
        # Auto-set updated_at timestamp
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.utcnow()
        else:
            update["$set"] = {"updated_at": datetime.utcnow()}

        result = await self.collection.update_one(
            {"_id": ObjectId(doc_id)}, update
        )
        return result.modified_count > 0

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document by query. Returns True if modified."""
        result = await self.collection.update_one(query, update)
        return result.modified_count > 0

    async def upsert_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> str:
        """Upsert a document. Returns the document ID."""
        result = await self.collection.update_one(query, update, upsert=True)
        return str(result.upserted_id) if result.upserted_id else None

    # ─── Delete ───────────────────────────────────────────

    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted."""
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    async def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete multiple documents. Returns count of deleted."""
        result = await self.collection.delete_many(query)
        return result.deleted_count

    # ─── Aggregation ──────────────────────────────────────

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run an aggregation pipeline."""
        results = []
        async for doc in self.collection.aggregate(pipeline):
            if "_id" in doc and isinstance(doc["_id"], ObjectId):
                doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    # ─── Utility ──────────────────────────────────────────

    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if any document matches the query."""
        return await self.collection.count_documents(query, limit=1) > 0
