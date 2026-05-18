"""
═══════════════════════════════════════════════════════════
RecruitAI — FastAPI Application Factory
═══════════════════════════════════════════════════════════
Main entry point. Initializes the app with middleware,
exception handlers, CORS, database connections, and routes.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import (
    RecruitAIException,
    recruitai_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.db.connection import MongoDB
from app.db.redis import RedisManager
from app.api.v1.router import api_v1_router

from loguru import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown events."""
    # ─── Startup ──────────────────────────────────────────
    setup_logging()
    logger.info(f"🚀 Starting {settings.APP_NAME} ({settings.APP_ENV})")

    await MongoDB.connect()
    await RedisManager.connect()

    logger.info(f"✅ {settings.APP_NAME} is ready!")

    yield

    # ─── Shutdown ─────────────────────────────────────────
    logger.info(f"🛑 Shutting down {settings.APP_NAME}...")
    await MongoDB.disconnect()
    await RedisManager.disconnect()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-powered recruitment optimization platform. "
            "Dynamically personalize resumes, score ATS compatibility, "
            "match jobs, and optimize application strategies."
        ),
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ─── CORS ─────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Custom Middleware ────────────────────────────────
    application.add_middleware(RequestLoggingMiddleware)

    # ─── Exception Handlers ───────────────────────────────
    application.add_exception_handler(RecruitAIException, recruitai_exception_handler)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    # ─── API Routes ───────────────────────────────────────
    application.include_router(api_v1_router, prefix=f"/api/{settings.API_VERSION}")

    return application


# Create the app instance
app = create_app()
