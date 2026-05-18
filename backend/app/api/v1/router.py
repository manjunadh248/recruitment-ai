"""
═══════════════════════════════════════════════════════════
RecruitAI — API v1 Router
═══════════════════════════════════════════════════════════
Aggregates all v1 API route modules into a single router.
"""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.resume import router as resume_router

api_v1_router = APIRouter()

# ─── Mount Sub-routers ────────────────────────────────────
api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(resume_router, prefix="/resume", tags=["Resume"])

# Future routers (uncomment as built in later phases):
# from app.api.v1.ats import router as ats_router
# from app.api.v1.personalize import router as personalize_router
# from app.api.v1.jobs import router as jobs_router
#
# api_v1_router.include_router(ats_router, prefix="/ats", tags=["ATS Scoring"])
# api_v1_router.include_router(personalize_router, prefix="/personalize", tags=["Personalization"])
# api_v1_router.include_router(jobs_router, prefix="/jobs", tags=["Job Matching"])
