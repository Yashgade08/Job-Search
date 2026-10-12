"""
Public Company Career Boards Adapter (Greenhouse Public Boards)
Crawls public, authorized job postings from official tech company career pages
(e.g., GitLab, Automattic, Figma, Docker, Stripe).
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from bs4 import BeautifulSoup
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapter.greenhouse")

# Permitted public career boards
DEFAULT_TARGET_COMPANIES = [
    "gitlab",
    "automattic",
    "docker",
    "hashicorp",
    "datadog",
]


class GreenhouseCareerAdapter(BaseCrawlerAdapter):
    def get_source_name(self) -> str:
        return "CompanyCareerBoards"

    def get_base_url(self) -> str:
        return "https://boards-api.greenhouse.io"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 2,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        companies = DEFAULT_TARGET_COMPANIES[:max_pages]

        for company in companies:
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
            if log_callback:
                log_callback("INFO", f"Crawling public career board for {company.title()} ({api_url})", 200)

            frontier.add_url(
                url=api_url,
                source_name=f"{company.title()} Careers",
                priority=2,
                depth=0
            )

            status_code, body, meta = self.fetch_page(api_url)
            if status_code != 200 or not body:
                if log_callback:
                    log_callback("WARNING", f"Status {status_code} fetching {company} career board", status_code)
                continue

            try:
                data = json.loads(body)
                job_list = data.get("jobs", [])
                
                # Filter for technical or queried positions
                for job in job_list:
                    title = job.get("title", "")
                    if query and query.lower() not in title.lower():
                        continue

                    job_url = job.get("absolute_url") or f"https://boards.greenhouse.io/{company}/jobs/{job.get('id')}"
                    frontier.add_url(url=job_url, source_name=f"{company.title()} Careers", priority=5, depth=1)

                    raw_content = job.get("content") or ""
                    location_name = job.get("location", {}).get("name", "Remote")
                    
                    # Clean HTML content
                    soup = BeautifulSoup(raw_content, "html.parser")
                    cleaned_text = soup.get_text(separator=" ")

                    posting_time = None
                    if job.get("updated_at"):
                        try:
                            posting_time = datetime.fromisoformat(job["updated_at"].replace("Z", "+00:00"))
                        except Exception:
                            posting_time = datetime.utcnow()

                    job_record = {
                        "job_title": title,
                        "company": company.title(),
                        "location_raw": location_name,
                        "city": "Remote" if "remote" in location_name.lower() else location_name.split(",")[0].strip(),
                        "country": "United States" if "us" in location_name.lower() or "usa" in location_name.lower() else "Global",
                        "is_remote": "remote" in location_name.lower(),
                        "salary_min": None,
                        "salary_max": None,
                        "salary_currency": "USD",
                        "salary_period": "yearly",
                        "experience_min_years": None,
                        "experience_max_years": None,
                        "experience_level": None,
                        "description_raw": raw_content,
                        "description_cleaned": cleaned_text,
                        "raw_html": raw_content[:50000] if raw_content else "",
                        "posting_date": posting_time or datetime.utcnow(),
                        "job_url": job_url,
                        "source_portal": f"{company.title()} Careers",
                    }
                    extracted_jobs.append(job_record)

                if log_callback:
                    log_callback("INFO", f"Extracted {len(job_list)} live job postings from {company.title()}", 200)

            except Exception as e:
                logger.error(f"Error parsing greenhouse feed for {company}: {e}")
                if log_callback:
                    log_callback("ERROR", f"Error parsing {company} career page: {e}", 500)

        return extracted_jobs
