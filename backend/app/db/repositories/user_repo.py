"""
═══════════════════════════════════════════════════════════
RecruitAI — User Repository
═══════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, Any
from app.db.repositories.base import BaseRepository
from app.models.user import UserDocument, UserResponse
from app.core.security import hash_password


class UserRepository(BaseRepository):
    collection_name = "users"

    async def create_user(self, email: str, password: str, name: str) -> str:
        """Create a new user with hashed password."""
        doc = UserDocument(
            email=email,
            name=name,
            password_hash=hash_password(password),
        )
        return await self.insert_one(doc.model_dump())

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email address."""
        return await self.find_one({"email": email})

    async def get_user_response(self, doc_id: str) -> Optional[UserResponse]:
        """Get a user as an API response object."""
        doc = await self.find_by_id(doc_id)
        if not doc:
            return None
        return UserResponse(
            id=doc["_id"],
            email=doc["email"],
            name=doc["name"],
            phone=doc.get("phone"),
            location=doc.get("location"),
            headline=doc.get("headline"),
            linkedin_url=doc.get("linkedin_url"),
            github_url=doc.get("github_url"),
            portfolio_url=doc.get("portfolio_url"),
            target_roles=doc.get("target_roles", []),
            experience_years=doc.get("experience_years"),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    async def update_profile(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile fields."""
        # Filter out None values
        clean = {k: v for k, v in updates.items() if v is not None}
        if not clean:
            return False
        return await self.update_by_id(doc_id, {"$set": clean})

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        return await self.exists({"email": email})


# Singleton instance
user_repo = UserRepository()
