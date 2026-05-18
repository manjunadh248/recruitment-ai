"""
═══════════════════════════════════════════════════════════
RecruitAI — Authentication API Routes
═══════════════════════════════════════════════════════════
Endpoints for user registration, login, token refresh,
and profile management. All responses use standardized
APIResponse wrappers.
"""

from fastapi import APIRouter, Depends, Body
from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    AuthTokenResponse,
)
from app.models.common import APIResponse
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_user, get_current_user_id

router = APIRouter()


# ═════════════════════════════════════════════════════════
# PUBLIC ENDPOINTS (no auth required)
# ═════════════════════════════════════════════════════════


@router.post(
    "/register",
    response_model=APIResponse,
    status_code=201,
    summary="Register a new account",
    description="Create a new user account and receive JWT tokens.",
)
async def register(req: UserRegisterRequest):
    """Register a new user with email and password."""
    result = await auth_service.register(req)
    return APIResponse(
        success=True,
        message="Account created successfully",
        data=result.model_dump(),
    )


@router.post(
    "/login",
    response_model=APIResponse,
    summary="Login to existing account",
    description="Authenticate with email/password and receive JWT tokens.",
)
async def login(req: UserLoginRequest):
    """Login with email and password."""
    result = await auth_service.login(req)
    return APIResponse(
        success=True,
        message="Login successful",
        data=result.model_dump(),
    )


@router.post(
    "/refresh",
    response_model=APIResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh_token(
    refresh_token: str = Body(..., embed=True, description="The refresh token"),
):
    """Get a new access token using a refresh token."""
    result = await auth_service.refresh_token(refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed",
        data=result,
    )


# ═════════════════════════════════════════════════════════
# PROTECTED ENDPOINTS (auth required)
# ═════════════════════════════════════════════════════════


@router.get(
    "/me",
    response_model=APIResponse,
    summary="Get current user profile",
    description="Returns the authenticated user's profile information.",
)
async def get_me(user_id: str = Depends(get_current_user_id)):
    """Get the current authenticated user's profile."""
    profile = await auth_service.get_profile(user_id)
    return APIResponse(
        success=True,
        message="Profile retrieved",
        data=profile.model_dump(),
    )


@router.patch(
    "/me",
    response_model=APIResponse,
    summary="Update current user profile",
    description="Update profile fields for the authenticated user.",
)
async def update_me(
    req: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Update the current user's profile."""
    profile = await auth_service.update_profile(user_id, req)
    return APIResponse(
        success=True,
        message="Profile updated",
        data=profile.model_dump(),
    )
