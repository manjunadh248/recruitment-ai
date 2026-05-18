"""
═══════════════════════════════════════════════════════════
RecruitAI — Resume API Routes
═══════════════════════════════════════════════════════════
Endpoints for resume upload, retrieval, deletion,
and primary-resume management. All endpoints require
JWT authentication.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from app.models.common import APIResponse
from app.services.resume_service import resume_service
from app.core.dependencies import get_current_user_id

router = APIRouter()


# ═════════════════════════════════════════════════════════
# RESUME ENDPOINTS (all protected)
# ═════════════════════════════════════════════════════════


@router.post(
    "/upload",
    response_model=APIResponse,
    status_code=201,
    summary="Upload and parse a resume",
    description=(
        "Upload a PDF or DOCX resume file. The file is parsed by the AI engine "
        "to extract structured data (skills, experience, education, etc.). "
        "The first uploaded resume is automatically set as primary."
    ),
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (PDF or DOCX)"),
    user_id: str = Depends(get_current_user_id),
):
    """Upload and parse a resume file."""
    result = await resume_service.upload_resume(user_id, file)
    return APIResponse(
        success=True,
        message="Resume uploaded and parsed successfully",
        data=result.model_dump(),
    )


@router.get(
    "/",
    response_model=APIResponse,
    summary="List all resumes",
    description="Get a list of all resumes uploaded by the authenticated user.",
)
async def list_resumes(
    user_id: str = Depends(get_current_user_id),
):
    """Get all resumes for the current user."""
    resumes = await resume_service.get_user_resumes(user_id)
    return APIResponse(
        success=True,
        message=f"Found {len(resumes)} resume(s)",
        data=[r.model_dump() for r in resumes],
    )


@router.get(
    "/{resume_id}",
    response_model=APIResponse,
    summary="Get resume details",
    description="Get full details of a specific resume including all parsed data.",
)
async def get_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a single resume with full parsed data."""
    resume = await resume_service.get_resume(user_id, resume_id)
    return APIResponse(
        success=True,
        message="Resume retrieved",
        data=resume.model_dump(),
    )


@router.delete(
    "/{resume_id}",
    response_model=APIResponse,
    summary="Delete a resume",
    description=(
        "Delete a resume and its associated file. If the deleted resume was "
        "the primary resume, another resume will be automatically set as primary."
    ),
)
async def delete_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a resume."""
    await resume_service.delete_resume(user_id, resume_id)
    return APIResponse(
        success=True,
        message="Resume deleted successfully",
    )


@router.patch(
    "/{resume_id}/primary",
    response_model=APIResponse,
    summary="Set resume as primary",
    description="Set a specific resume as the user's primary resume for ATS scoring and personalization.",
)
async def set_primary_resume(
    resume_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Set a resume as primary."""
    await resume_service.set_primary(user_id, resume_id)
    return APIResponse(
        success=True,
        message="Resume set as primary",
    )
