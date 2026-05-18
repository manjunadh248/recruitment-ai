"""
═══════════════════════════════════════════════════════════
RecruitAI — Authentication Service
═══════════════════════════════════════════════════════════
Business logic for user registration, login, token refresh,
and profile management. Keeps route handlers thin.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from loguru import logger

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
    NotFoundException,
    BadRequestException,
)
from app.db.repositories.user_repo import user_repo
from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    AuthTokenResponse,
)


class AuthService:
    """Handles authentication business logic."""

    # ─── Registration ─────────────────────────────────────

    async def register(self, req: UserRegisterRequest) -> AuthTokenResponse:
        """Register a new user and return tokens."""
        # Check for existing email
        if await user_repo.email_exists(req.email):
            raise ConflictException("An account with this email already exists")

        # Create user
        user_id = await user_repo.create_user(
            email=req.email,
            password=req.password,
            name=req.name,
        )
        logger.info(f"New user registered: {req.email} (id={user_id})")

        # Generate tokens
        tokens = self._generate_tokens(user_id)

        # Fetch fresh user for response
        user_response = await user_repo.get_user_response(user_id)

        return AuthTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            user=user_response,
        )

    # ─── Login ────────────────────────────────────────────

    async def login(self, req: UserLoginRequest) -> AuthTokenResponse:
        """Authenticate user and return tokens."""
        # Find user by email
        user = await user_repo.find_by_email(req.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Verify password
        if not verify_password(req.password, user["password_hash"]):
            raise UnauthorizedException("Invalid email or password")

        # Check active status
        if not user.get("is_active", True):
            raise UnauthorizedException("Account is deactivated")

        user_id = user["_id"]
        logger.info(f"User logged in: {req.email}")

        # Generate tokens
        tokens = self._generate_tokens(user_id)

        # Build response
        user_response = await user_repo.get_user_response(user_id)

        return AuthTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            user=user_response,
        )

    # ─── Token Refresh ────────────────────────────────────

    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Validate a refresh token and return a new access token."""
        payload = decode_token(refresh_token)
        if payload is None:
            raise UnauthorizedException("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type. Expected refresh token.")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Token payload missing subject")

        # Verify user still exists and is active
        user = await user_repo.find_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        if not user.get("is_active", True):
            raise UnauthorizedException("Account is deactivated")

        # Generate new access token only
        access_token = create_access_token(data={"sub": user_id})

        logger.info(f"Token refreshed for user: {user_id}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    # ─── Profile ──────────────────────────────────────────

    async def get_profile(self, user_id: str) -> UserResponse:
        """Get user profile by ID."""
        user_response = await user_repo.get_user_response(user_id)
        if not user_response:
            raise NotFoundException("User")
        return user_response

    async def update_profile(
        self, user_id: str, req: UserUpdateRequest
    ) -> UserResponse:
        """Update user profile fields."""
        updates = req.model_dump(exclude_none=True)
        if not updates:
            raise BadRequestException("No fields to update")

        success = await user_repo.update_profile(user_id, updates)
        if not success:
            raise NotFoundException("User")

        logger.info(f"Profile updated for user: {user_id}")
        return await user_repo.get_user_response(user_id)

    # ─── Helpers ──────────────────────────────────────────

    def _generate_tokens(self, user_id: str) -> Dict[str, str]:
        """Generate access + refresh token pair."""
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


# Singleton instance
auth_service = AuthService()
