"""
═══════════════════════════════════════════════════════════
RecruitAI — Middleware Stack
═══════════════════════════════════════════════════════════
Request logging, rate limiting, and processing time tracking.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = f"{time.time_ns()}"

        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"[{request.client.host if request.client else 'unknown'}] "
            f"rid={request_id}"
        )

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(process_time)
        response.headers["X-Request-ID"] = request_id

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time}ms"
        )

        return response
