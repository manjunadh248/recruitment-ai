"""
═══════════════════════════════════════════════════════════
RecruitAI — Exception Handlers
═══════════════════════════════════════════════════════════
Centralized exception handling for consistent error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger


class RecruitAIException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)


class NotFoundException(RecruitAIException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404, "NOT_FOUND")


class BadRequestException(RecruitAIException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, 400, "BAD_REQUEST")


class UnauthorizedException(RecruitAIException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401, "UNAUTHORIZED")


class ForbiddenException(RecruitAIException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403, "FORBIDDEN")


class ConflictException(RecruitAIException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409, "CONFLICT")


async def recruitai_exception_handler(request: Request, exc: RecruitAIException):
    """Handle all RecruitAI custom exceptions."""
    logger.warning(f"⚠️  {exc.error_code}: {exc.message} [{request.url.path}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"⚠️  HTTP {exc.status_code}: {exc.detail} [{request.url.path}]")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"🔥 Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "error_code": "INTERNAL_ERROR",
        },
    )
