"""
Job Processing Pipeline
Executes data cleaning, title normalization, NLP skill extraction, deduplication,
and database persistence.
"""

import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from nlp.title_normalizer import normalize_job_title, extract_experience_years
from nlp.skill_extractor import skill_extractor
from crawler.frontier import normalize_canonical_url
from crawler.deduplication import generate_content_fingerprint
from database.repository import save_job_record, is_duplicate_job
from database.connection import session_scope

logger = logging.getLogger("job_crawler.pipeline")


class JobProcessingPipeline:
    def __init__(self):
        pass

    def process_item(self, item: Dict[str, Any], session: Optional[Session] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Processes a raw extracted job item.
        Returns: (status: 'saved' | 'duplicate' | 'invalid', result_dict)
        """
        job_title = (item.get("job_title") or "").strip()
        company = (item.get("company") or "").strip()
        job_url = (item.get("job_url") or "").strip()

        # Validation
        if not job_title or not job_url:
            return "invalid", {"reason": "Missing job_title or job_url"}

        # Canonicalize URL
        canonical_url = normalize_canonical_url(job_url)
        
        # Clean Description
        raw_desc = item.get("description_raw") or ""
        cleaned_desc = skill_extractor.clean_text(raw_desc or item.get("description_cleaned", ""))

        # Generate unique content fingerprint
        location_raw = item.get("location_raw") or ""
        fingerprint = generate_content_fingerprint(
            title=job_title,
            company=company,
            location=location_raw,
            description_snippet=cleaned_desc
        )

        # NLP Title & Seniority Normalization
        norm_title, role_cat, exp_level = normalize_job_title(job_title)
        
        # If experience level or years were not extracted by adapter, extract from text
        exp_min = item.get("experience_min_years")
        exp_max = item.get("experience_max_years")
        if exp_min is None and exp_max is None:
            t_min, t_max = extract_experience_years(f"{job_title} {cleaned_desc[:1000]}")
            exp_min = t_min
            exp_max = t_max

        # Salary fallback if adapter didn't find structured salary
        sal_min = item.get("salary_min")
        sal_max = item.get("salary_max")
        sal_curr = item.get("salary_currency", "USD")
        if sal_min is None and sal_max is None:
            s_min, s_max, s_curr = skill_extractor.extract_salary_fallback(cleaned_desc)
            if s_min is not None:
                sal_min = s_min
                sal_max = s_max
                sal_curr = s_curr

        # NLP Skill Extraction
        extracted_skills = skill_extractor.extract_skills_from_text(cleaned_desc, title=job_title)

        # Build clean job dictionary
        cleaned_job_record = {
            "fingerprint": fingerprint,
            "job_title": job_title,
            "company": company or "Confidential",
            "location_raw": location_raw,
            "normalized_title": norm_title,
            "role_category": role_cat,
            "city": item.get("city"),
            "state": item.get("state"),
            "country": item.get("country"),
            "is_remote": bool(item.get("is_remote", False)),
            "salary_min": sal_min,
            "salary_max": sal_max,
            "salary_currency": sal_curr,
            "salary_period": item.get("salary_period", "yearly"),
            "experience_min_years": exp_min,
            "experience_max_years": exp_max,
            "experience_level": item.get("experience_level") or exp_level,
            "description_raw": raw_desc,
            "description_cleaned": cleaned_desc,
            "raw_html": item.get("raw_html"),
            "posting_date": item.get("posting_date") or datetime.utcnow(),
            "job_url": job_url,
            "canonical_url": canonical_url,
            "source_portal": item.get("source_portal", "Generic"),
            "crawl_run_id": item.get("crawl_run_id"),
        }

        # Database persistence
        if session is not None:
            job_obj, is_new = save_job_record(session, cleaned_job_record, extracted_skills)
            status = "saved" if is_new else "duplicate"
            cleaned_job_record["id"] = job_obj.id if job_obj else None
            cleaned_job_record["extracted_skills"] = extracted_skills
            return status, cleaned_job_record
        else:
            with session_scope() as sess:
                job_obj, is_new = save_job_record(sess, cleaned_job_record, extracted_skills)
                status = "saved" if is_new else "duplicate"
                cleaned_job_record["id"] = job_obj.id if job_obj else None
                cleaned_job_record["extracted_skills"] = extracted_skills
                return status, cleaned_job_record


pipeline = JobProcessingPipeline()
