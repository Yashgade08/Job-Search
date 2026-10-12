"""
Skill Extraction and Requirement Parsing Engine
Extracts technical and soft skills, requirement vs preferred classification,
and salary/experience indicators from text.
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from bs4 import BeautifulSoup
from nlp.taxonomy import SKILL_TAXONOMY, SKILL_BY_NAME


# Section boundary patterns for Required vs Preferred qualifications
REQUIRED_SECTION_PATTERNS = re.compile(
    r"(?:requirements|what\s+you(?:'ll|\s+will)\s+need|qualifications|must\s+haves?|basic\s+qualifications|what\s+we\s+expect|what\s+you\s+bring)\b",
    re.I
)

PREFERRED_SECTION_PATTERNS = re.compile(
    r"(?:nice\s+to\s+have|preferred\s+qualifications|bonus\s+points?|what\s+is\s+a\s+plus|good\s+to\s+have|desired\s+skills|pluses)\b",
    re.I
)

SALARY_REGEX = re.compile(
    r"(\$|€|£|₹|INR|USD|EUR|GBP)\s*(\d{1,3}(?:[,\.]\d{3})*|\d+)(?:k|K)?\s*(?:-|to)\s*(\$|€|£|₹|INR|USD|EUR|GBP)?\s*(\d{1,3}(?:[,\.]\d{3})*|\d+)(?:k|K)?",
    re.I
)


class SkillExtractor:
    def __init__(self):
        self._compiled_skills = []
        self._build_compiled_patterns()

    def _build_compiled_patterns(self):
        for entry in SKILL_TAXONOMY:
            name = entry["name"]
            category = entry["category"]
            is_tech = entry["is_tech"]
            aliases = entry.get("aliases", [])
            custom_regex = entry.get("regex")

            patterns = []
            if custom_regex:
                patterns.append(re.compile(custom_regex, re.I))
            else:
                # Escape special regex characters in skill name if any
                escaped_name = re.escape(name)
                patterns.append(re.compile(rf"\b{escaped_name}\b", re.I))

            for alias in aliases:
                if alias.strip():
                    patterns.append(re.compile(rf"\b{re.escape(alias.strip())}\b", re.I))

            self._compiled_skills.append({
                "canonical_name": name,
                "category": category,
                "is_tech": is_tech,
                "patterns": patterns,
            })

    def clean_text(self, text: str) -> str:
        """Strip HTML tags, markdown links, and excess whitespaces."""
        if not text:
            return ""
        # If contains HTML tags, parse with BeautifulSoup
        if "<" in text and ">" in text:
            try:
                soup = BeautifulSoup(text, "html.parser")
                text = soup.get_text(separator=" ")
            except Exception:
                pass
        
        # Replace non-breaking spaces and tabs
        text = text.replace("\xa0", " ").replace("\t", " ")
        # Collapse multiple spaces and lines
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def segment_requirements_sections(self, text: str) -> Tuple[str, str, str]:
        """
        Segments text into: (general_text, required_section, preferred_section)
        """
        lower = text.lower()
        req_start = -1
        pref_start = -1

        req_match = REQUIRED_SECTION_PATTERNS.search(lower)
        if req_match:
            req_start = req_match.start()

        pref_match = PREFERRED_SECTION_PATTERNS.search(lower)
        if pref_match:
            pref_start = pref_match.start()

        # Cases of ordering
        general_text = text
        required_text = ""
        preferred_text = ""

        if req_start != -1 and pref_start != -1:
            if req_start < pref_start:
                general_text = text[:req_start]
                required_text = text[req_start:pref_start]
                preferred_text = text[pref_start:]
            else:
                general_text = text[:pref_start]
                preferred_text = text[pref_start:req_start]
                required_text = text[req_start:]
        elif req_start != -1:
            general_text = text[:req_start]
            required_text = text[req_start:]
        elif pref_start != -1:
            general_text = text[:pref_start]
            preferred_text = text[pref_start:]

        return general_text, required_text, preferred_text

    def extract_skills_from_text(self, text: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Extracts all identified skills from description and job title.
        Assigns is_required based on section location or title emphasis.
        """
        if not text and not title:
            return []

        cleaned_desc = self.clean_text(text)
        cleaned_title = self.clean_text(title)
        
        # Segment sections
        general_sec, req_sec, pref_sec = self.segment_requirements_sections(cleaned_desc)

        extracted: Dict[str, Dict[str, Any]] = {}

        for item in self._compiled_skills:
            canonical = item["canonical_name"]
            category = item["category"]
            is_tech = item["is_tech"]
            patterns = item["patterns"]

            total_matches = 0
            found_in_title = False
            found_in_req = False
            found_in_pref = False
            found_in_gen = False

            # Check title first (high confidence)
            for p in patterns:
                m = p.findall(cleaned_title)
                if m:
                    found_in_title = True
                    total_matches += len(m)

            # Check preferred section
            if pref_sec:
                for p in patterns:
                    m = p.findall(pref_sec)
                    if m:
                        found_in_pref = True
                        total_matches += len(m)

            # Check required section
            if req_sec:
                for p in patterns:
                    m = p.findall(req_sec)
                    if m:
                        found_in_req = True
                        total_matches += len(m)

            # Check general text
            if general_sec:
                for p in patterns:
                    m = p.findall(general_sec)
                    if m:
                        found_in_gen = True
                        total_matches += len(m)

            if total_matches > 0:
                # Determine is_required:
                # If found in preferred section ONLY, then is_required = False.
                # If found in title, required section, or general section, is_required = True.
                is_req = True
                if found_in_pref and not (found_in_title or found_in_req or found_in_gen):
                    is_req = False

                confidence = 1.0 if (found_in_title or total_matches > 1) else 0.85

                extracted[canonical] = {
                    "name": canonical,
                    "category": category,
                    "is_tech": is_tech,
                    "is_required": is_req,
                    "confidence": confidence,
                    "count": total_matches,
                }

        return list(extracted.values())

    def extract_salary_fallback(self, text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Attempts to extract salary numbers from text if not present in metadata.
        Returns: (min_salary, max_salary, currency)
        """
        match = SALARY_REGEX.search(text)
        if not match:
            return None, None, None

        curr1, val1_raw, curr2, val2_raw = match.groups()
        raw_curr = curr1 or curr2 or "USD"
        curr_map = {"$": "USD", "€": "EUR", "£": "GBP", "₹": "INR"}
        currency = curr_map.get(raw_curr, raw_curr.upper())
        
        # Clean numeric
        try:
            val1_str = val1_raw.replace(",", "")
            val2_str = val2_raw.replace(",", "")
            val1 = float(val1_str)
            val2 = float(val2_str)

            # Adjust if in thousands (e.g. 120 -> 120000 or if 'k' was in text)
            if val1 < 1000 and "k" in match.group(0).lower():
                val1 *= 1000
                val2 *= 1000
            elif val1 < 500 and ("yr" in text.lower() or "year" in text.lower() or "annum" in text.lower()):
                val1 *= 1000
                val2 *= 1000

            return min(val1, val2), max(val1, val2), currency
        except Exception:
            return None, None, None


# Singleton instance
skill_extractor = SkillExtractor()
