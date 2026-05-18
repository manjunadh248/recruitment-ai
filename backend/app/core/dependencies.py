"""
═══════════════════════════════════════════════════════════
RecruitAI — Auth Dependencies
═══════════════════════════════════════════════════════════
FastAPI dependency injection for authentication.
Extracts and validates JWT tokens from request headers,
returning the current authenticated user.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token
from app.db.repositories.user_repo import user_repo
from app.models.user import UserResponse

# Bearer token extractor
security_scheme = HTTPBearer(
    scheme_name="JWT",
    description="Enter your JWT access token",
    auto_error=True,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """
    Dependency that extracts the JWT from the Authorization header,
    validates it, and returns the full user document from MongoDB.

    Usage:
        @router.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["_id"]}
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use an access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject",
        )

    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


async def get_current_user_id(
    user: dict = Depends(get_current_user),
) -> str:
    """Lightweight dependency that returns just the user ID string."""
    return user["_id"]


async def get_current_user_response(
    user: dict = Depends(get_current_user),
) -> UserResponse:
    """Dependency that returns a clean UserResponse object."""
    return UserResponse(
        id=user["_id"],
        email=user["email"],
        name=user["name"],
        phone=user.get("phone"),
        location=user.get("location"),
        headline=user.get("headline"),
        linkedin_url=user.get("linkedin_url"),
        github_url=user.get("github_url"),
        portfolio_url=user.get("portfolio_url"),
        target_roles=user.get("target_roles", []),
        experience_years=user.get("experience_years"),
        created_at=user["created_at"],
        updated_at=user.get("updated_at"),
    )
