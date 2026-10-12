"""
Arbeitnow Permitted Tech Jobs Crawler Adapter
Crawls authorized public tech jobs with full HTML descriptions, tags, and locations.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapter.arbeitnow")


class ArbeitnowAdapter(BaseCrawlerAdapter):
    def get_source_name(self) -> str:
        return "Arbeitnow"

    def get_base_url(self) -> str:
        return "https://www.arbeitnow.com"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 5,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        base_api_url = "https://www.arbeitnow.com/api/job-board-api"

        for page in range(1, max_pages + 1):
            page_url = f"{base_api_url}?page={page}"
            if log_callback:
                log_callback("INFO", f"Discovering URLs from Arbeitnow page {page}", 200)

            # Discover URL in frontier
            frontier.add_url(
                url=page_url,
                source_name=self.get_source_name(),
                priority=1,
                depth=0,
                meta={"page": page}
            )

            status_code, body, meta = self.fetch_page(page_url)
            if status_code != 200 or not body:
                if log_callback:
                    log_callback("WARNING", f"Failed fetching Arbeitnow page {page} with status {status_code}", status_code)
                break

            try:
                data = json.loads(body)
                job_list = data.get("data", [])
                if not job_list:
                    if log_callback:
                        log_callback("INFO", f"No more jobs on Arbeitnow page {page}. Concluded discovery.", 200)
                    break

                for item in job_list:
                    job_url = item.get("url") or f"{self.get_base_url()}/jobs/{item.get('slug')}"
                    
                    # Add job detail URL to frontier
                    frontier.add_url(
                        url=job_url,
                        source_name=self.get_source_name(),
                        priority=5,
                        depth=1
                    )

                    posting_time = None
                    if item.get("created_at"):
                        try:
                            posting_time = datetime.fromtimestamp(item["created_at"])
                        except Exception:
                            posting_time = datetime.utcnow()

                    tags = item.get("tags") or []
                    tags_text = ", ".join(tags)
                    raw_desc = item.get("description") or ""
                    full_desc = f"{raw_desc} \n\nTags: {tags_text}"

                    job_record = {
                        "job_title": item.get("title", "Software Developer"),
                        "company": item.get("company_name", "Confidential"),
                        "location_raw": item.get("location", "Remote"),
                        "city": item.get("location") if item.get("location") and "remote" not in item.get("location", "").lower() else "Remote",
                        "country": "Germany / Remote",
                        "is_remote": bool(item.get("remote", False)),
                        "salary_min": None,
                        "salary_max": None,
                        "salary_currency": "EUR",
                        "salary_period": "yearly",
                        "experience_min_years": None,
                        "experience_max_years": None,
                        "experience_level": None,
                        "description_raw": raw_desc,
                        "raw_html": raw_desc if len(raw_desc) < 50000 else raw_desc[:50000],
                        "posting_date": posting_time,
                        "job_url": job_url,
                        "source_portal": self.get_source_name(),
                    }
                    extracted_jobs.append(job_record)

                if log_callback:
                    log_callback("INFO", f"Extracted {len(job_list)} jobs from Arbeitnow page {page}", 200)

                # Check if next page exists
                if not data.get("links", {}).get("next"):
                    break

            except json.JSONDecodeError as e:
                logger.error(f"Failed decoding JSON from Arbeitnow: {e}")
                if log_callback:
                    log_callback("ERROR", f"JSON decode error: {e}", 500)
                break

        return extracted_jobs
