"""
═══════════════════════════════════════════════════════════
RecruitAI — Health Check Endpoints
═══════════════════════════════════════════════════════════
System health and readiness checks for monitoring.
"""

from fastapi import APIRouter
from app.core.config import get_settings
from app.db.connection import MongoDB
from app.db.redis import RedisManager
from app.models.common import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check.
    Verifies MongoDB and Redis connectivity.
    """
    mongo_status = "unknown"
    redis_status = "unknown"

    # Check MongoDB
    try:
        await MongoDB.get_db().command("ping")
        mongo_status = "connected"
    except Exception:
        mongo_status = "disconnected"

    # Check Redis
    try:
        await RedisManager.get_client().ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    overall = "healthy" if mongo_status == "connected" and redis_status == "connected" else "degraded"

    return HealthResponse(
        status=overall,
        app_name=settings.APP_NAME,
        version="1.0.0",
        environment=settings.APP_ENV,
        mongodb=mongo_status,
        redis=redis_status,
    )
