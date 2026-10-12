"""
Job Deduplication and Content Fingerprinting Engine
Prevents duplicate ingestion across cross-posted listings, re-crawled URLs,
and minor whitespace/tracking variations.
"""

import hashlib
import re
from typing import Dict, Any, Set
from crawler.frontier import normalize_canonical_url


def generate_content_fingerprint(
    title: str,
    company: str,
    location: str = "",
    description_snippet: str = ""
) -> str:
    """
    Computes a deterministic 64-character SHA-256 hash of normalized core attributes:
    title + company + location + first 300 alphanumeric characters of description.
    """
    clean_title = re.sub(r"[^a-z0-9]", "", (title or "").lower())
    clean_company = re.sub(r"[^a-z0-9]", "", (company or "").lower())
    clean_location = re.sub(r"[^a-z0-9]", "", (location or "").lower())
    clean_desc = re.sub(r"[^a-z0-9]", "", (description_snippet or "").lower())[:300]

    raw_payload = f"{clean_title}|{clean_company}|{clean_location}|{clean_desc}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def generate_url_fingerprint(url: str) -> str:
    """Computes SHA-256 hash of the canonical URL."""
    canonical = normalize_canonical_url(url)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Computes word-level Jaccard similarity between two text snippets."""
    words1 = set(re.findall(r"\w+", (text1 or "").lower()))
    words2 = set(re.findall(r"\w+", (text2 or "").lower()))
    if not words1 or not words2:
        return 0.0
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    return round(intersection / union, 3) if union > 0 else 0.0


class DeduplicationFilter:
    """In-memory cache for fast deduplication within crawl runs."""
    def __init__(self):
        self._seen_fingerprints: Set[str] = set()
        self._seen_canonical_urls: Set[str] = set()

    def is_duplicate(self, fingerprint: str, canonical_url: str) -> bool:
        if fingerprint in self._seen_fingerprints or canonical_url in self._seen_canonical_urls:
            return True
        return False

    def mark_seen(self, fingerprint: str, canonical_url: str):
        self._seen_fingerprints.add(fingerprint)
        self._seen_canonical_urls.add(canonical_url)

    def count(self) -> int:
        return len(self._seen_fingerprints)
