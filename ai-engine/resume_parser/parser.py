"""
═══════════════════════════════════════════════════════════
RecruitAI — Resume Parser (Orchestrator)
═══════════════════════════════════════════════════════════
Main parser class that orchestrates text extraction,
section detection, and entity extraction to produce a
fully structured ParsedResumeData object.
"""

from typing import Optional
from loguru import logger

from ai_engine.resume_parser.text_extractor import extract_text
from ai_engine.resume_parser.section_detector import detect_sections
from ai_engine.resume_parser.entity_extractor import (
    extract_contact_info,
    extract_skills,
    extract_education,
    extract_experience,
    extract_projects,
    extract_certifications,
    extract_languages,
)


class ResumeParser:
    """
    Orchestrates the full resume parsing pipeline:
    1. Extract raw text from PDF/DOCX
    2. Detect and split sections
    3. Extract structured entities from each section
    4. Return a ParsedResumeData-compatible dict
    """

    def parse(self, file_path: str, file_type: str) -> dict:
        """
        Parse a resume file into structured data.

        Args:
            file_path: Absolute path to the resume file
            file_type: File extension ('pdf' or 'docx')

        Returns:
            Tuple of (parsed_data_dict, raw_text)
        """
        logger.info(f"🔍 Parsing resume: {file_path} (type={file_type})")

        # Step 1: Extract raw text
        try:
            raw_text = extract_text(file_path, file_type)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return self._empty_result(), ""

        if not raw_text or len(raw_text.strip()) < 20:
            logger.warning("Extracted text is too short or empty")
            return self._empty_result(), raw_text or ""

        logger.info(f"📄 Extracted {len(raw_text)} characters of text")

        # Step 2: Detect sections
        try:
            sections = detect_sections(raw_text)
        except Exception as e:
            logger.error(f"Section detection failed: {e}")
            sections = {"header": raw_text}

        logger.info(f"📑 Detected sections: {list(sections.keys())}")

        # Step 3: Extract entities from each section
        parsed_data = self._extract_all_entities(sections, raw_text)

        # Log summary
        skills_count = len(parsed_data.get("skills", []))
        edu_count = len(parsed_data.get("education", []))
        exp_count = len(parsed_data.get("experience", []))
        logger.info(
            f"✅ Parsing complete — Skills: {skills_count}, "
            f"Education: {edu_count}, Experience: {exp_count}"
        )

        return parsed_data, raw_text

    def _extract_all_entities(self, sections: dict, raw_text: str) -> dict:
        """Extract all entity types from the detected sections."""
        parsed = {}

        # Contact Info — from header section
        try:
            header_text = sections.get("header", "")
            contact = extract_contact_info(header_text or raw_text[:500])
            parsed["contact_info"] = contact
        except Exception as e:
            logger.warning(f"Contact extraction failed: {e}")
            parsed["contact_info"] = {}

        # Summary
        try:
            summary_text = sections.get("summary", "")
            if summary_text:
                # Clean and truncate summary
                parsed["summary"] = summary_text.strip()[:1000]
        except Exception as e:
            logger.warning(f"Summary extraction failed: {e}")

        # Skills
        try:
            skills_text = sections.get("skills", "")
            parsed["skills"] = extract_skills(skills_text, raw_text)
        except Exception as e:
            logger.warning(f"Skills extraction failed: {e}")
            parsed["skills"] = []

        # Education
        try:
            education_text = sections.get("education", "")
            parsed["education"] = extract_education(education_text)
        except Exception as e:
            logger.warning(f"Education extraction failed: {e}")
            parsed["education"] = []

        # Experience
        try:
            experience_text = sections.get("experience", "")
            parsed["experience"] = extract_experience(experience_text)
        except Exception as e:
            logger.warning(f"Experience extraction failed: {e}")
            parsed["experience"] = []

        # Projects
        try:
            projects_text = sections.get("projects", "")
            parsed["projects"] = extract_projects(projects_text)
        except Exception as e:
            logger.warning(f"Projects extraction failed: {e}")
            parsed["projects"] = []

        # Certifications
        try:
            certs_text = sections.get("certifications", "")
            parsed["certifications"] = extract_certifications(certs_text)
        except Exception as e:
            logger.warning(f"Certifications extraction failed: {e}")
            parsed["certifications"] = []

        # Languages
        try:
            langs_text = sections.get("languages", "")
            parsed["languages"] = extract_languages(langs_text)
        except Exception as e:
            logger.warning(f"Languages extraction failed: {e}")
            parsed["languages"] = []

        # Estimate total experience years
        try:
            parsed["total_experience_years"] = self._estimate_experience_years(
                parsed.get("experience", [])
            )
        except Exception:
            parsed["total_experience_years"] = None

        return parsed

    def _estimate_experience_years(self, experiences: list) -> Optional[float]:
        """
        Rough estimate of total experience years based on date ranges.
        Returns None if cannot be determined.
        """
        import re
        from datetime import datetime

        total_months = 0

        for exp in experiences:
            start = exp.get("start_date", "")
            end = exp.get("end_date", "")

            if not start:
                continue

            start_year = self._extract_year(start)
            if not start_year:
                continue

            if exp.get("is_current") or (end and re.search(r"present|current|now", end, re.IGNORECASE)):
                end_year = datetime.now().year
            else:
                end_year = self._extract_year(end)

            if start_year and end_year:
                months = max(0, (end_year - start_year) * 12)
                total_months += months

        if total_months > 0:
            return round(total_months / 12, 1)
        return None

    @staticmethod
    def _extract_year(date_str: str) -> Optional[int]:
        """Extract a 4-digit year from a date string."""
        import re
        match = re.search(r"(\d{4})", date_str)
        if match:
            year = int(match.group(1))
            if 1970 <= year <= 2030:
                return year
        return None

    @staticmethod
    def _empty_result() -> dict:
        """Return an empty parsed data structure."""
        return {
            "contact_info": {},
            "summary": None,
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "total_experience_years": None,
        }


# Singleton instance
resume_parser = ResumeParser()
