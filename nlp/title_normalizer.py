"""
Job Title Normalization and Seniority Classification Engine
Maps non-standard job titles to canonical software and data roles.
"""

import re
from typing import Dict, Any, Tuple, Optional


# Canonical Role Categories and Matching Patterns
ROLE_PATTERNS = [
    (
        "VLSI / Semiconductor Engineer",
        re.compile(r"\b(?:vlsi|asic|fpga|rtl\s+design|physical\s+design|verification\s+engineer|silicon\s+engineer|chip\s+design|semiconductor|soc\s+design|sta\s+engineer|uvm\s+engineer|hardware\s+engineer)\b", re.I)
    ),
    (
        "Consultant / Advisory",
        re.compile(r"\b(?:consultant|technology\s+consultant|it\s+consultant|strategy\s+consultant|management\s+consultant|advisory\s+consultant|solution\s+consultant|sap\s+consultant|associate\s+consultant|principal\s+consultant|business\s+consultant)\b", re.I)
    ),
    (
        "Machine Learning Engineer",
        re.compile(r"\b(?:machine\s+learning|ml\s+engineer|mle|deep\s+learning\s+engineer|nlp\s+engineer|computer\s+vision\s+engineer|ai\s+engineer|generative\s+ai\s+engineer)\b", re.I)
    ),
    (
        "Data Scientist",
        re.compile(r"\b(?:data\s+scientist|applied\s+scientist|research\s+scientist|decision\s+scientist|statistician)\b", re.I)
    ),
    (
        "Data Engineer",
        re.compile(r"\b(?:data\s+engineer|big\s+data\s+engineer|etl\s+developer|analytics\s+engineer|bi\s+developer|data\s+platform\s+engineer)\b", re.I)
    ),
    (
        "DevOps / SRE",
        re.compile(r"\b(?:devops|sre|site\s+reliability|platform\s+engineer|infrastructure\s+engineer|cloud\s+engineer|systems\s+engineer|kubernetes\s+engineer)\b", re.I)
    ),
    (
        "Cloud Architect",
        re.compile(r"\b(?:cloud\s+architect|solutions\s+architect|enterprise\s+architect|software\s+architect|system\s+architect)\b", re.I)
    ),
    (
        "Frontend Developer",
        re.compile(r"\b(?:front[\s-]?end|ui[\s-]?developer|react\s+developer|angular\s+developer|vue\s+developer|web\s+developer|ui/ux\s+engineer)\b", re.I)
    ),
    (
        "Backend Developer",
        re.compile(r"\b(?:back[\s-]?end|python\s+developer|java\s+developer|golang\s+developer|node(?:\.js)?\s+developer|\.net\s+developer|c\+\+\s+developer|django\s+developer|spring\s+developer)\b", re.I)
    ),
    (
        "Software Development Engineer (SDE / SWE)",
        re.compile(r"\b(?:sde[\s-]?[123i]{1,3}|sde|swe|software\s+development\s+engineer|software\s+engineer|software\s+developer|core\s+software\s+engineer|swe[\s-]?[123i]{1,3})\b", re.I)
    ),
    (
        "Full Stack Developer",
        re.compile(r"\b(?:full[\s-]?stack|fullstack|application\s+developer|programmer)\b", re.I)
    ),
    (
        "Mobile Developer",
        re.compile(r"\b(?:mobile\s+developer|ios\s+developer|android\s+developer|flutter\s+developer|react\s+native\s+developer)\b", re.I)
    ),
    (
        "Security Engineer",
        re.compile(r"\b(?:security\s+engineer|cybersecurity|infosec|application\s+security|appsec|cloud\s+security|soc\s+analyst)\b", re.I)
    ),
    (
        "QA / Test Automation",
        re.compile(r"\b(?:qa|quality\s+assurance|sdet|test\s+automation|automation\s+engineer|test\s+engineer)\b", re.I)
    ),
    (
        "Product Manager",
        re.compile(r"\b(?:product\s+manager|technical\s+product\s+manager|tpm|program\s+manager|project\s+manager)\b", re.I)
    ),
    (
        "Engineering Manager",
        re.compile(r"\b(?:engineering\s+manager|tech\s+lead|team\s+lead|director\s+of\s+engineering|vp\s+of\s+engineering|head\s+of\s+engineering)\b", re.I)
    ),
]

# Seniority Level Patterns
SENIORITY_PATTERNS = [
    ("Executive", re.compile(r"\b(?:vp|vice\s+president|director|head\s+of|chief|cxo|cto|cpo)\b", re.I)),
    ("Lead / Staff", re.compile(r"\b(?:lead|staff|principal|distinguished|architect|tech\s+lead|sde[\s-]?3|sde\s+iii|principal\s+consultant)\b", re.I)),
    ("Senior", re.compile(r"\b(?:senior|sr\.?|sr|iii|advanced|senior\s+consultant)\b", re.I)),
    ("Entry-Level", re.compile(r"\b(?:junior|jr\.?|jr|entry|associate|trainee|intern|internship|graduate|sde[\s-]?1|sde\s+i|associate\s+consultant)\b", re.I)),
]

EXPERIENCE_YEARS_REGEX = re.compile(
    r"(?:(\d{1,2})\s*(?:-|to)\s*(\d{1,2})|\b(\d{1,2})\s*\+?)\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?",
    re.I
)


def normalize_job_title(raw_title: str) -> Tuple[str, str, str]:
    """
    Analyzes raw job title and returns:
    (normalized_title, role_category, experience_level)
    """
    if not raw_title or not raw_title.strip():
        return ("Software Engineer", "Full Stack Developer", "Mid-Level")

    cleaned_title = raw_title.strip()

    # 1. Detect Seniority Level
    experience_level = "Mid-Level"
    for level_name, pat in SENIORITY_PATTERNS:
        if pat.search(cleaned_title):
            experience_level = level_name
            break

    # 2. Detect Role Category
    role_category = "Full Stack Developer"
    for category_name, pat in ROLE_PATTERNS:
        if pat.search(cleaned_title):
            role_category = category_name
            break

    # 3. Construct clean standardized title
    if experience_level in ["Senior", "Lead / Staff"]:
        prefix = experience_level.split(" / ")[0]
        normalized_title = f"{prefix} {role_category}"
    elif experience_level == "Entry-Level":
        normalized_title = f"Junior {role_category}"
    elif experience_level == "Executive":
        normalized_title = f"{role_category} (Leadership)"
    else:
        normalized_title = role_category

    return normalized_title, role_category, experience_level


def extract_experience_years(text: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts min and max years of experience from job title or description text.
    E.g., "3-5 years" -> (3.0, 5.0), "5+ years" -> (5.0, None)
    """
    if not text:
        return None, None

    match = EXPERIENCE_YEARS_REGEX.search(text)
    if not match:
        return None, None

    g1, g2, g3 = match.groups()
    if g1 and g2:
        return float(g1), float(g2)
    elif g3:
        return float(g3), None

    return None, None
