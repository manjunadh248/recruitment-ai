"""
═══════════════════════════════════════════════════════════
RecruitAI — Section Detector
═══════════════════════════════════════════════════════════
Splits raw resume text into semantic sections by detecting
common resume headings and their variations.
"""

import re
from typing import Dict, List, Tuple, Optional
from loguru import logger


# ─── Section Heading Patterns ─────────────────────────────
# Maps canonical section names to regex patterns that match
# common heading variations in resumes.

SECTION_PATTERNS: Dict[str, List[str]] = {
    "summary": [
        r"summary",
        r"professional\s+summary",
        r"career\s+summary",
        r"executive\s+summary",
        r"profile",
        r"professional\s+profile",
        r"career\s+profile",
        r"objective",
        r"career\s+objective",
        r"about\s+me",
        r"about",
        r"overview",
    ],
    "experience": [
        r"experience",
        r"work\s+experience",
        r"professional\s+experience",
        r"employment\s+history",
        r"employment",
        r"work\s+history",
        r"career\s+history",
        r"relevant\s+experience",
        r"professional\s+background",
    ],
    "education": [
        r"education",
        r"academic\s+background",
        r"academic\s+qualifications",
        r"qualifications",
        r"educational\s+background",
        r"academics",
    ],
    "skills": [
        r"skills",
        r"technical\s+skills",
        r"core\s+competencies",
        r"competencies",
        r"key\s+skills",
        r"areas\s+of\s+expertise",
        r"expertise",
        r"technologies",
        r"tools\s+(?:and|&)\s+technologies",
        r"programming\s+languages",
        r"tech\s+stack",
    ],
    "projects": [
        r"projects",
        r"personal\s+projects",
        r"academic\s+projects",
        r"key\s+projects",
        r"selected\s+projects",
        r"notable\s+projects",
        r"side\s+projects",
    ],
    "certifications": [
        r"certifications",
        r"certificates",
        r"professional\s+certifications",
        r"licenses\s+(?:and|&)\s+certifications",
        r"credentials",
    ],
    "languages": [
        r"languages",
        r"language\s+proficiency",
        r"language\s+skills",
    ],
    "awards": [
        r"awards",
        r"honors",
        r"awards\s+(?:and|&)\s+honors",
        r"achievements",
        r"accomplishments",
    ],
    "publications": [
        r"publications",
        r"research",
        r"research\s+(?:and|&)\s+publications",
        r"papers",
    ],
    "volunteer": [
        r"volunteer",
        r"volunteer\s+experience",
        r"volunteering",
        r"community\s+involvement",
        r"community\s+service",
    ],
    "interests": [
        r"interests",
        r"hobbies",
        r"hobbies\s+(?:and|&)\s+interests",
        r"extracurricular",
        r"extracurricular\s+activities",
        r"activities",
    ],
    "references": [
        r"references",
        r"professional\s+references",
    ],
}


def _build_heading_regex() -> re.Pattern:
    """
    Build a single compiled regex that matches any known section heading.
    Headings are detected as lines that:
      - Start at the beginning of a line
      - Contain a known heading phrase
      - Are typically short (< 60 chars)
      - May be followed by a colon
      - May be ALL CAPS or Title Case
    """
    all_patterns = []
    for patterns in SECTION_PATTERNS.values():
        all_patterns.extend(patterns)

    # Build alternation pattern
    alternation = "|".join(all_patterns)
    # Match lines that look like headings
    heading_re = re.compile(
        rf"^[\s]*(?:[-•=_*#]{{0,5}}\s*)?({alternation})[\s:.\-—]*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return heading_re


HEADING_REGEX = _build_heading_regex()


def _classify_heading(heading_text: str) -> Optional[str]:
    """Map a detected heading string to its canonical section name."""
    heading_clean = heading_text.strip().lower()
    heading_clean = re.sub(r"[:\-—._*#]", "", heading_clean).strip()

    for section_name, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.fullmatch(pattern, heading_clean, re.IGNORECASE):
                return section_name
    return None


def detect_sections(raw_text: str) -> Dict[str, str]:
    """
    Split raw resume text into named sections.

    Returns a dict mapping section names to their text content.
    Text before any detected heading goes into 'header' section
    (usually contains name and contact info).

    Args:
        raw_text: The full extracted resume text

    Returns:
        Dict like {"header": "...", "summary": "...", "experience": "...", ...}
    """
    sections: Dict[str, str] = {}
    matches: List[Tuple[int, int, str]] = []

    # Find all heading matches with their positions
    for match in HEADING_REGEX.finditer(raw_text):
        heading_text = match.group(1)
        section_name = _classify_heading(heading_text)
        if section_name:
            matches.append((match.start(), match.end(), section_name))

    if not matches:
        # No sections detected — treat entire text as header
        logger.warning("No section headings detected in resume text")
        sections["header"] = raw_text.strip()
        return sections

    # Sort by position
    matches.sort(key=lambda x: x[0])

    # Extract header (text before first heading)
    header_text = raw_text[: matches[0][0]].strip()
    if header_text:
        sections["header"] = header_text

    # Extract each section's content
    for i, (start, end, section_name) in enumerate(matches):
        # Content starts after the heading line
        content_start = end
        # Content ends at the start of the next heading (or end of text)
        content_end = matches[i + 1][0] if i + 1 < len(matches) else len(raw_text)
        content = raw_text[content_start:content_end].strip()

        if content:
            # If section already exists, append
            if section_name in sections:
                sections[section_name] += "\n\n" + content
            else:
                sections[section_name] = content

    logger.info(f"Detected {len(sections)} sections: {list(sections.keys())}")
    return sections
