"""
═══════════════════════════════════════════════════════════
RecruitAI — AI Engine: Resume Parser Module
═══════════════════════════════════════════════════════════
Extracts structured data from PDF/DOCX resumes using
NLP (spaCy) and semantic analysis (sentence-transformers).
"""

from ai_engine.resume_parser.parser import ResumeParser, resume_parser

__all__ = ["ResumeParser", "resume_parser"]
