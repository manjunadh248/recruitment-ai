"""
═══════════════════════════════════════════════════════════
RecruitAI — Logging Configuration
═══════════════════════════════════════════════════════════
Structured logging using Loguru with JSON output for
production and pretty-print for development.
"""

import sys
from loguru import logger
from app.core.config import get_settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    if settings.is_production:
        # Production: JSON format for log aggregation
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,
        )
        logger.add(
            "logs/recruitai.log",
            rotation="50 MB",
            retention="30 days",
            compression="gz",
            level="INFO",
            serialize=True,
        )
    else:
        # Development: Pretty colored output
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG",
            colorize=True,
        )

    logger.info(f"🚀 Logging initialized — env={settings.APP_ENV}")
