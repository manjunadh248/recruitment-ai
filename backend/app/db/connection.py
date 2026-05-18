"""
═══════════════════════════════════════════════════════════
RecruitAI — MongoDB Connection Manager
═══════════════════════════════════════════════════════════
Async MongoDB client using Motor with connection lifecycle
management tied to the FastAPI app lifespan.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from app.core.config import get_settings

settings = get_settings()


class MongoDB:
    """Singleton MongoDB connection manager."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize the MongoDB connection."""
        logger.info(f"🔌 Connecting to MongoDB: {settings.MONGODB_DB_NAME}")
        cls.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        cls.db = cls.client[settings.MONGODB_DB_NAME]

        # Verify connection
        await cls.client.admin.command("ping")
        logger.info("✅ MongoDB connected successfully")

    @classmethod
    async def disconnect(cls) -> None:
        """Close the MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("🔌 MongoDB connection closed")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if cls.db is None:
            raise RuntimeError("MongoDB is not connected. Call connect() first.")
        return cls.db

    @classmethod
    def get_collection(cls, name: str):
        """Get a specific collection."""
        return cls.get_db()[name]


async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get the database instance."""
    return MongoDB.get_db()
