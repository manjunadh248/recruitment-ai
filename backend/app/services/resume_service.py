"""
═══════════════════════════════════════════════════════════
RecruitAI — Resume Service
═══════════════════════════════════════════════════════════
Business logic for resume upload, parsing, retrieval,
deletion, and primary-resume management. Keeps route
handlers thin by encapsulating all orchestration here.
"""

import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import UploadFile
from loguru import logger

from app.core.config import get_settings
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)
from app.db.repositories.resume_repo import resume_repo
from app.models.resume import (
    ResumeDocument,
    ParsedResumeData,
    ResumeUploadResponse,
    ResumeListItem,
    ContactInfo,
    Education,
    Experience,
    Project,
    Certification,
)

settings = get_settings()

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class ResumeService:
    """Handles all resume-related business logic."""

    # ─── Upload & Parse ──────────────────────────────────

    async def upload_resume(
        self, user_id: str, file: UploadFile
    ) -> ResumeUploadResponse:
        """
        Upload a resume file, parse it with AI, and store in MongoDB.

        1. Validate file type and size
        2. Save file to disk
        3. Invoke AI parser
        4. Store parsed data in MongoDB
        5. Auto-set as primary if first resume
        """
        # Validate file
        self._validate_file(file)

        # Determine file type
        file_type = self._get_file_type(file.filename)

        # Save file to disk
        file_path = await self._save_file(user_id, file)
        logger.info(f"File saved: {file_path}")

        # Parse with AI engine
        parsed_data, raw_text = await self._parse_resume(file_path, file_type)

        # Check if this is the first resume (auto-set primary)
        existing_count = await resume_repo.count({"user_id": user_id})
        is_primary = existing_count == 0

        # Create database document
        doc = ResumeDocument(
            user_id=user_id,
            filename=file.filename,
            file_type=file_type,
            file_path=file_path,
            raw_text=raw_text,
            parsed_data=parsed_data,
            is_primary=is_primary,
            created_at=datetime.utcnow(),
        )

        # Store in MongoDB
        doc_id = await resume_repo.create_resume(doc)
        logger.info(f"Resume stored in DB: {doc_id} (primary={is_primary})")

        return doc.to_response(doc_id)

    # ─── Retrieval ────────────────────────────────────────

    async def get_user_resumes(self, user_id: str) -> List[ResumeListItem]:
        """Get all resumes for a user as brief list items."""
        docs = await resume_repo.get_user_resumes(user_id)
        items = []
        for doc in docs:
            items.append(
                ResumeListItem(
                    id=doc["_id"],
                    filename=doc["filename"],
                    file_type=doc["file_type"],
                    skills_count=len(doc.get("parsed_data", {}).get("skills", [])),
                    is_primary=doc.get("is_primary", False),
                    created_at=doc["created_at"],
                )
            )
        return items

    async def get_resume(
        self, user_id: str, resume_id: str
    ) -> ResumeUploadResponse:
        """Get a single resume with full parsed data. Checks ownership."""
        doc = await resume_repo.find_by_id(resume_id)
        if not doc:
            raise NotFoundException("Resume")

        if doc["user_id"] != user_id:
            raise ForbiddenException("You do not own this resume")

        # Reconstruct ParsedResumeData from stored dict
        parsed_dict = doc.get("parsed_data", {})

        return ResumeUploadResponse(
            id=doc["_id"],
            user_id=doc["user_id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            parsed_data=self._dict_to_parsed_data(parsed_dict),
            skills_count=len(parsed_dict.get("skills", [])),
            is_primary=doc.get("is_primary", False),
            created_at=doc["created_at"],
        )

    # ─── Delete ───────────────────────────────────────────

    async def delete_resume(self, user_id: str, resume_id: str) -> bool:
        """Delete a resume and its file. Checks ownership."""
        doc = await resume_repo.find_by_id(resume_id)
        if not doc:
            raise NotFoundException("Resume")

        if doc["user_id"] != user_id:
            raise ForbiddenException("You do not own this resume")

        # Delete file from disk
        file_path = doc.get("file_path", "")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except OSError as e:
                logger.warning(f"Failed to delete file {file_path}: {e}")

        # Delete from database
        deleted = await resume_repo.delete_by_id(resume_id)

        # If deleted resume was primary, set another as primary
        if doc.get("is_primary") and deleted:
            remaining = await resume_repo.get_user_resumes(user_id, limit=1)
            if remaining:
                await resume_repo.set_primary(user_id, remaining[0]["_id"])
                logger.info(f"New primary resume set: {remaining[0]['_id']}")

        return deleted

    # ─── Set Primary ──────────────────────────────────────

    async def set_primary(self, user_id: str, resume_id: str) -> bool:
        """Set a resume as the user's primary resume."""
        doc = await resume_repo.find_by_id(resume_id)
        if not doc:
            raise NotFoundException("Resume")

        if doc["user_id"] != user_id:
            raise ForbiddenException("You do not own this resume")

        return await resume_repo.set_primary(user_id, resume_id)

    # ─── Private Helpers ──────────────────────────────────

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size."""
        if not file.filename:
            raise BadRequestException("No filename provided")

        file_ext = self._get_file_type(file.filename)
        if file_ext not in ALLOWED_EXTENSIONS:
            raise BadRequestException(
                f"Unsupported file type: .{file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Check content type
        if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
            # Some browsers send generic content types, so just warn
            logger.warning(f"Unexpected content type: {file.content_type}")

    @staticmethod
    def _get_file_type(filename: str) -> str:
        """Extract file extension from filename."""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    async def _save_file(self, user_id: str, file: UploadFile) -> str:
        """
        Save uploaded file to disk in the user's upload directory.
        Returns the absolute file path.
        """
        # Create user upload directory
        upload_dir = Path(settings.UPLOAD_DIR) / user_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename to avoid collisions
        file_ext = self._get_file_type(file.filename)
        unique_name = f"{uuid.uuid4().hex[:12]}_{file.filename}"
        file_path = upload_dir / unique_name

        # Check file size while writing
        total_size = 0
        max_size = settings.max_file_size_bytes

        try:
            with open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 64):  # 64KB chunks
                    total_size += len(chunk)
                    if total_size > max_size:
                        # Clean up partial file
                        f.close()
                        os.remove(file_path)
                        raise BadRequestException(
                            f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
                        )
                    f.write(chunk)
        except BadRequestException:
            raise
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise BadRequestException(f"Failed to save file: {e}")

        return str(file_path.absolute())

    async def _parse_resume(self, file_path: str, file_type: str) -> tuple:
        """
        Invoke the AI engine resume parser.
        Returns (ParsedResumeData, raw_text).
        """
        try:
            from ai_engine.resume_parser import resume_parser

            parsed_dict, raw_text = resume_parser.parse(file_path, file_type)
            parsed_data = self._dict_to_parsed_data(parsed_dict)
            return parsed_data, raw_text
        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            # Return empty parsed data so upload still succeeds
            return ParsedResumeData(), ""

    @staticmethod
    def _dict_to_parsed_data(data: dict) -> ParsedResumeData:
        """Convert a raw dict to a ParsedResumeData model."""
        contact_raw = data.get("contact_info", {})
        contact = ContactInfo(**contact_raw) if isinstance(contact_raw, dict) else ContactInfo()

        education = []
        for edu in data.get("education", []):
            try:
                education.append(Education(**edu))
            except Exception:
                pass

        experience = []
        for exp in data.get("experience", []):
            try:
                experience.append(Experience(**exp))
            except Exception:
                pass

        projects = []
        for proj in data.get("projects", []):
            try:
                projects.append(Project(**proj))
            except Exception:
                pass

        certifications = []
        for cert in data.get("certifications", []):
            try:
                certifications.append(Certification(**cert))
            except Exception:
                pass

        return ParsedResumeData(
            contact_info=contact,
            summary=data.get("summary"),
            skills=data.get("skills", []),
            education=education,
            experience=experience,
            projects=projects,
            certifications=certifications,
            languages=data.get("languages", []),
            total_experience_years=data.get("total_experience_years"),
        )


# Singleton instance
resume_service = ResumeService()
