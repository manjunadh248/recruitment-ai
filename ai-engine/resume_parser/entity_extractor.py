"""
═══════════════════════════════════════════════════════════
RecruitAI — Entity Extractor
═══════════════════════════════════════════════════════════
Extracts structured entities (contact info, skills, education,
experience, projects, certifications) from sectioned resume text.
"""

import re
from typing import Dict, List, Optional, Tuple
from loguru import logger


# ─── Contact Info Patterns ────────────────────────────────

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[\s\-.]?)?"
    r"(?:\(?\d{2,4}\)?[\s\-.]?)"
    r"\d{3,4}[\s\-.]?\d{3,4}"
)

LINKEDIN_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?",
    re.IGNORECASE,
)

GITHUB_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?",
    re.IGNORECASE,
)

PORTFOLIO_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?[\w\-]+\.(?:dev|io|com|me|tech|site|app|xyz)/?\S*",
    re.IGNORECASE,
)

# ─── Date Patterns ────────────────────────────────────────

DATE_RANGE_REGEX = re.compile(
    r"("
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"[\s,]*\d{4}"
    r"|"
    r"\d{1,2}/\d{4}"
    r"|"
    r"\d{4}"
    r")"
    r"\s*(?:[-–—to]+|to)\s*"
    r"("
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"[\s,]*\d{4}"
    r"|"
    r"\d{1,2}/\d{4}"
    r"|"
    r"\d{4}"
    r"|"
    r"[Pp]resent|[Cc]urrent|[Nn]ow|[Oo]ngoing"
    r")",
    re.IGNORECASE,
)

SINGLE_DATE_REGEX = re.compile(
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"[\s,]*\d{4}",
    re.IGNORECASE,
)


# ─── Common Skills Database ──────────────────────────────

COMMON_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "haskell", "lua", "dart", "elixir",
    "objective-c", "assembly", "visual basic", "groovy", "clojure",

    # Web Frontend
    "html", "css", "react", "react.js", "reactjs", "angular",
    "angular.js", "angularjs", "vue", "vue.js", "vuejs", "svelte",
    "next.js", "nextjs", "nuxt.js", "nuxtjs", "gatsby",
    "tailwind", "tailwindcss", "bootstrap", "sass", "scss", "less",
    "webpack", "vite", "jquery", "redux", "mobx", "zustand",
    "material ui", "chakra ui", "shadcn", "framer motion",

    # Web Backend
    "node.js", "nodejs", "express", "express.js", "expressjs",
    "django", "flask", "fastapi", "spring", "spring boot",
    ".net", "asp.net", "rails", "ruby on rails", "laravel",
    "gin", "fiber", "actix", "rocket", "phoenix", "nestjs",
    "graphql", "rest", "restful", "grpc", "websocket",

    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
    "elasticsearch", "cassandra", "dynamodb", "firebase",
    "sqlite", "oracle", "sql server", "mariadb", "couchdb",
    "neo4j", "influxdb", "supabase", "prisma", "mongoose",
    "sequelize", "typeorm", "sqlalchemy",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "k8s", "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "ci/cd", "nginx", "apache", "heroku", "vercel",
    "netlify", "digitalocean", "cloudflare", "linux", "unix",
    "bash", "shell", "powershell", "vagrant", "helm",
    "prometheus", "grafana", "datadog", "new relic", "cloudwatch",

    # AI / ML / Data
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "jupyter", "opencv", "hugging face", "transformers",
    "langchain", "openai", "gpt", "bert", "llm",
    "data science", "data engineering", "data analysis",
    "data visualization", "big data", "spark", "hadoop",
    "kafka", "airflow", "dbt", "snowflake", "databricks",
    "tableau", "power bi", "looker", "metabase",

    # Mobile
    "react native", "flutter", "ios", "android",
    "swiftui", "jetpack compose", "xamarin", "cordova", "ionic",

    # Tools & Practices
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "figma", "sketch", "adobe xd", "photoshop", "illustrator",
    "postman", "swagger", "agile", "scrum", "kanban",
    "tdd", "bdd", "unit testing", "integration testing",
    "jest", "mocha", "pytest", "cypress", "selenium",
    "microservices", "monolith", "event-driven", "serverless",
    "design patterns", "oop", "functional programming",
    "data structures", "algorithms", "system design",
}


def extract_contact_info(text: str) -> dict:
    """
    Extract contact information from resume header text.
    Returns a dict with email, phone, linkedin_url, github_url,
    portfolio_url, and location fields.
    """
    contact = {}

    # Email
    email_match = EMAIL_REGEX.search(text)
    if email_match:
        contact["email"] = email_match.group(0).lower()

    # Phone
    phone_match = PHONE_REGEX.search(text)
    if phone_match:
        contact["phone"] = phone_match.group(0).strip()

    # LinkedIn
    linkedin_match = LINKEDIN_REGEX.search(text)
    if linkedin_match:
        url = linkedin_match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        contact["linkedin_url"] = url

    # GitHub
    github_match = GITHUB_REGEX.search(text)
    if github_match:
        url = github_match.group(0)
        if not url.startswith("http"):
            url = "https://" + url
        contact["github_url"] = url

    # Portfolio (exclude LinkedIn and GitHub matches)
    for match in PORTFOLIO_REGEX.finditer(text):
        url = match.group(0)
        if "linkedin.com" not in url.lower() and "github.com" not in url.lower():
            if not url.startswith("http"):
                url = "https://" + url
            contact["portfolio_url"] = url
            break

    # Location — heuristic: look for City, State/Country patterns
    location_patterns = [
        r"(?:^|\n)\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2}(?:\s+\d{5})?)\s*(?:\n|$)",
        r"(?:^|\n)\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*(?:\n|$)",
    ]
    for pattern in location_patterns:
        loc_match = re.search(pattern, text)
        if loc_match:
            location = loc_match.group(1).strip()
            # Filter out false positives
            if len(location) < 60 and not EMAIL_REGEX.search(location):
                contact["location"] = location
                break

    logger.debug(f"Extracted contact info: {list(contact.keys())}")
    return contact


def extract_skills(text: str, all_text: str = "") -> List[str]:
    """
    Extract skills from the skills section and full resume text.
    Uses a curated skills database for matching.

    Args:
        text: The skills section text specifically
        all_text: The full resume text for additional matching
    """
    found_skills = set()
    combined = (text + " " + all_text).lower()

    # Match against known skills database
    for skill in COMMON_SKILLS:
        # Use word boundary matching to avoid partial matches
        pattern = r"(?:^|[\s,;|•/\-(])(?:" + re.escape(skill) + r")(?:[\s,;|•/\-)]|$)"
        if re.search(pattern, combined, re.IGNORECASE):
            found_skills.add(skill)

    # Also extract comma/bullet separated items from skills section
    if text:
        # Split by common delimiters
        items = re.split(r"[,;|•·\n]", text)
        for item in items:
            clean = item.strip().strip("-").strip("•").strip("*").strip()
            if clean and 2 <= len(clean) <= 40:
                # Check if it looks like a skill (not a sentence)
                if len(clean.split()) <= 4:
                    found_skills.add(clean.lower())

    # Deduplicate similar skills
    skills_list = sorted(found_skills)
    logger.debug(f"Extracted {len(skills_list)} skills")
    return skills_list


def extract_education(text: str) -> List[dict]:
    """
    Extract education entries from the education section.
    Returns a list of dicts matching the Education schema.
    """
    if not text:
        return []

    entries = []
    # Split into individual entries by double newline or date ranges
    blocks = re.split(r"\n\n+", text)

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue

        entry = {}
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            continue

        # Try to extract dates
        date_match = DATE_RANGE_REGEX.search(block)
        if date_match:
            entry["start_date"] = date_match.group(1).strip()
            end = date_match.group(2).strip()
            entry["end_date"] = end

        # Common degree patterns
        degree_patterns = [
            r"((?:Bachelor|Master|Doctor|Ph\.?D|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|"
            r"B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|MBA|BBA|BCA|MCA|"
            r"Associate|Diploma)[\w\s.,]*?)(?:\n|$|(?:from|at|in)\s)",
        ]
        for pattern in degree_patterns:
            deg_match = re.search(pattern, block, re.IGNORECASE)
            if deg_match:
                entry["degree"] = deg_match.group(1).strip().rstrip(",.- ")
                break

        # GPA
        gpa_match = re.search(
            r"(?:GPA|CGPA|Grade|Score)[\s:]*(\d+\.?\d*(?:\s*/\s*\d+\.?\d*)?)",
            block,
            re.IGNORECASE,
        )
        if gpa_match:
            entry["gpa"] = gpa_match.group(1).strip()

        # Institution — heuristic: usually the first or second line,
        # often contains "University", "Institute", "College", "School"
        for line in lines[:3]:
            if re.search(
                r"university|institute|college|school|academy|iit|nit|bits",
                line,
                re.IGNORECASE,
            ):
                entry["institution"] = re.sub(
                    r"\s*[\(\[].*?[\)\]]", "", line
                ).strip().rstrip(",.- ")
                break

        # If no institution found via keywords, use first line
        if "institution" not in entry and lines:
            entry["institution"] = lines[0].strip().rstrip(",.- ")

        # Field of study
        field_match = re.search(
            r"(?:in|of|–|-)\s+([\w\s&]+?)(?:\n|$|,|\()",
            block,
            re.IGNORECASE,
        )
        if field_match:
            field = field_match.group(1).strip()
            if len(field) > 3 and len(field) < 60:
                entry["field_of_study"] = field

        # Description — remaining lines
        desc_lines = [
            l for l in lines
            if l != entry.get("institution", "")
            and l != entry.get("degree", "")
        ]
        if desc_lines:
            entry["description"] = " ".join(desc_lines[:3])

        if entry.get("institution") or entry.get("degree"):
            entries.append(entry)

    logger.debug(f"Extracted {len(entries)} education entries")
    return entries


def extract_experience(text: str) -> List[dict]:
    """
    Extract work experience entries from the experience section.
    Returns a list of dicts matching the Experience schema.
    """
    if not text:
        return []

    entries = []

    # Split into individual entries — look for date range patterns as delimiters
    # First try double newline split
    blocks = re.split(r"\n\n+", text)

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue

        entry = {}
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            continue

        # Extract dates
        date_match = DATE_RANGE_REGEX.search(block)
        if date_match:
            entry["start_date"] = date_match.group(1).strip()
            end = date_match.group(2).strip()
            entry["end_date"] = end
            entry["is_current"] = bool(
                re.search(r"present|current|now|ongoing", end, re.IGNORECASE)
            )

        # Title — usually in first 2 lines, often contains common job title words
        title_keywords = [
            r"engineer", r"developer", r"manager", r"analyst", r"designer",
            r"architect", r"lead", r"director", r"intern", r"consultant",
            r"specialist", r"coordinator", r"executive", r"officer",
            r"associate", r"senior", r"junior", r"staff", r"principal",
            r"head\s+of", r"vp\s+of", r"vice\s+president",
        ]
        title_pattern = "|".join(title_keywords)
        for line in lines[:3]:
            if re.search(title_pattern, line, re.IGNORECASE):
                # Clean the line — remove dates
                clean_title = DATE_RANGE_REGEX.sub("", line).strip()
                clean_title = SINGLE_DATE_REGEX.sub("", clean_title).strip()
                clean_title = clean_title.strip("|-–—, ")
                if clean_title:
                    entry["title"] = clean_title
                    break

        # Company — look for company indicators or use first non-title line
        for line in lines[:3]:
            if line == entry.get("title"):
                continue
            # Often company lines have location info
            if re.search(r"(?:Inc|LLC|Ltd|Corp|Company|Technologies|Solutions|Labs|Studio)", line, re.IGNORECASE):
                entry["company"] = re.sub(r"\s*[\(\[].*?[\)\]]", "", line).strip().rstrip(",|- ")
                break

        # Fallback: use first line as company or title
        if "company" not in entry and "title" not in entry and lines:
            entry["title"] = lines[0].strip()
        elif "company" not in entry and lines:
            for line in lines[:2]:
                if line != entry.get("title"):
                    entry["company"] = line.strip().rstrip(",|- ")
                    break

        # Location
        loc_match = re.search(
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2}(?:\s+\d{5})?)",
            block,
        )
        if loc_match:
            entry["location"] = loc_match.group(1).strip()

        # Highlights — bullet points or lines starting with - • * ▪ ►
        highlights = []
        for line in lines:
            line_clean = line.strip()
            if re.match(r"^[-•*▪►◦‣⁃]\s+", line_clean):
                highlight = re.sub(r"^[-•*▪►◦‣⁃]\s+", "", line_clean).strip()
                if highlight and len(highlight) > 10:
                    highlights.append(highlight)
        entry["highlights"] = highlights

        # Description — combine non-bullet lines after title/company
        desc_lines = [
            l for l in lines[2:]
            if not re.match(r"^[-•*▪►◦‣⁃]\s+", l)
            and l.strip()
        ]
        if desc_lines:
            entry["description"] = " ".join(desc_lines[:3])

        if entry.get("title") or entry.get("company"):
            entries.append(entry)

    logger.debug(f"Extracted {len(entries)} experience entries")
    return entries


def extract_projects(text: str) -> List[dict]:
    """
    Extract project entries from the projects section.
    Returns a list of dicts matching the Project schema.
    """
    if not text:
        return []

    entries = []
    blocks = re.split(r"\n\n+", text)

    for block in blocks:
        block = block.strip()
        if not block or len(block) < 10:
            continue

        entry = {}
        lines = [l.strip() for l in block.split("\n") if l.strip()]

        if not lines:
            continue

        # Project name — usually first line
        entry["name"] = lines[0].strip().rstrip(",|- ")

        # URL
        url_match = re.search(r"https?://\S+", block)
        if url_match:
            entry["url"] = url_match.group(0).rstrip(".,;)")

        # Technologies — look for "Tech:", "Built with:", "Technologies:" patterns
        tech_match = re.search(
            r"(?:Tech(?:nolog(?:y|ies))?|Built\s+with|Stack|Tools?)[\s:]+(.+?)(?:\n|$)",
            block,
            re.IGNORECASE,
        )
        if tech_match:
            techs = re.split(r"[,;|•·]", tech_match.group(1))
            entry["technologies"] = [t.strip() for t in techs if t.strip()]
        else:
            # Try to find known technologies in the block
            found_techs = []
            block_lower = block.lower()
            for skill in COMMON_SKILLS:
                pattern = r"(?:^|[\s,;|•/\-(])" + re.escape(skill) + r"(?:[\s,;|•/\-)]|$)"
                if re.search(pattern, block_lower):
                    found_techs.append(skill)
            if found_techs:
                entry["technologies"] = found_techs[:10]

        # Highlights — bullet points
        highlights = []
        for line in lines[1:]:
            line_clean = line.strip()
            if re.match(r"^[-•*▪►◦‣⁃]\s+", line_clean):
                highlight = re.sub(r"^[-•*▪►◦‣⁃]\s+", "", line_clean).strip()
                if highlight:
                    highlights.append(highlight)
        entry["highlights"] = highlights

        # Description — first non-bullet line after title
        for line in lines[1:]:
            if not re.match(r"^[-•*▪►◦‣⁃]\s+", line):
                desc = line.strip()
                if desc and len(desc) > 15:
                    entry["description"] = desc
                    break

        if entry.get("name"):
            entries.append(entry)

    logger.debug(f"Extracted {len(entries)} project entries")
    return entries


def extract_certifications(text: str) -> List[dict]:
    """
    Extract certification entries from the certifications section.
    Returns a list of dicts matching the Certification schema.
    """
    if not text:
        return []

    entries = []
    # Split by newlines or bullets
    items = re.split(r"\n+", text)

    for item in items:
        item = item.strip().lstrip("-•*▪►◦‣⁃ ")
        if not item or len(item) < 5:
            continue

        entry = {}

        # Extract date
        date_match = SINGLE_DATE_REGEX.search(item)
        if date_match:
            entry["date"] = date_match.group(0).strip()
            item = SINGLE_DATE_REGEX.sub("", item).strip()

        # Extract URL
        url_match = re.search(r"https?://\S+", item)
        if url_match:
            entry["url"] = url_match.group(0).rstrip(".,;)")
            item = item.replace(url_match.group(0), "").strip()

        # Check for issuer patterns (e.g., "by Google", "- AWS", "| Coursera")
        issuer_match = re.search(
            r"(?:by|from|–|-|—|\|)\s+(.+?)(?:$|\(|\[)",
            item,
            re.IGNORECASE,
        )
        if issuer_match:
            entry["issuer"] = issuer_match.group(1).strip().rstrip(",.- ")
            item = item[: issuer_match.start()].strip()

        entry["name"] = item.strip().rstrip(",.-| ")

        if entry.get("name"):
            entries.append(entry)

    logger.debug(f"Extracted {len(entries)} certification entries")
    return entries


def extract_languages(text: str) -> List[str]:
    """Extract languages from the languages section."""
    if not text:
        return []

    languages = []
    items = re.split(r"[,;|\n•·]", text)
    for item in items:
        clean = item.strip().lstrip("-•*▪► ")
        # Remove proficiency levels
        clean = re.sub(
            r"\s*[\(\[:]?\s*(?:native|fluent|proficient|intermediate|"
            r"basic|beginner|advanced|conversational|working\s+proficiency|"
            r"professional|elementary)\s*[\)\]]?\s*",
            "",
            clean,
            flags=re.IGNORECASE,
        ).strip()
        if clean and 2 <= len(clean) <= 30:
            languages.append(clean)

    logger.debug(f"Extracted {len(languages)} languages")
    return languages
