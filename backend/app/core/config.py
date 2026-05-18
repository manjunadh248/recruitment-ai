"""
═══════════════════════════════════════════════════════════
RecruitAI — Application Configuration
═══════════════════════════════════════════════════════════
Centralized settings using Pydantic Settings for type-safe
environment variable loading with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    # ─── App ──────────────────────────────────────────────
    APP_NAME: str = "RecruitAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    SECRET_KEY: str = "change-me-in-production"

    # ─── JWT ──────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── MongoDB ──────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017/recruitai"
    MONGODB_DB_NAME: str = "recruitai"

    # ─── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── AI/LLM ──────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"  # "openai" or "gemini"

    # ─── File Storage ─────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    # ─── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loaded once per process."""
    return Settings()
