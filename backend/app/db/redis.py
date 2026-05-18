"""
═══════════════════════════════════════════════════════════
RecruitAI — Redis Connection Manager
═══════════════════════════════════════════════════════════
Async Redis client for caching, session storage,
and pub/sub event bus.
"""

import redis.asyncio as aioredis
from loguru import logger
from app.core.config import get_settings

settings = get_settings()


class RedisManager:
    """Singleton Redis connection manager."""

    client: aioredis.Redis = None

    @classmethod
    async def connect(cls) -> None:
        """Initialize the Redis connection."""
        logger.info("🔌 Connecting to Redis...")
        cls.client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        # Verify connection
        await cls.client.ping()
        logger.info("✅ Redis connected successfully")

    @classmethod
    async def disconnect(cls) -> None:
        """Close the Redis connection."""
        if cls.client:
            await cls.client.close()
            logger.info("🔌 Redis connection closed")

    @classmethod
    def get_client(cls) -> aioredis.Redis:
        """Get the Redis client instance."""
        if cls.client is None:
            raise RuntimeError("Redis is not connected. Call connect() first.")
        return cls.client


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency to get the Redis client."""
    return RedisManager.get_client()
