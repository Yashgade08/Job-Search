"""
Jobicy Public Tech Remote Jobs Adapter
Crawls authorized public engineering feeds from Jobicy API.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapter.jobicy")


class JobicyAdapter(BaseCrawlerAdapter):
    def get_source_name(self) -> str:
        return "Jobicy"

    def get_base_url(self) -> str:
        return "https://jobicy.com"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 2,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        count = min(50, max_pages * 20)
        api_url = f"https://jobicy.com/api/v2/remote-jobs?count={count}"
        if query:
            api_url += f"&tag={query}"

        if log_callback:
            log_callback("INFO", f"Requesting Jobicy public API feed: {api_url}", 200)

        frontier.add_url(url=api_url, source_name=self.get_source_name(), priority=1, depth=0)

        status_code, body, meta = self.fetch_page(api_url)
        if status_code != 200 or not body:
            if log_callback:
                log_callback("WARNING", f"Jobicy returned status {status_code}", status_code)
            return extracted_jobs

        try:
            data = json.loads(body)
            jobs_list = data.get("jobs", [])
            for item in jobs_list:
                job_url = item.get("url") or f"{self.get_base_url()}/jobs/{item.get('id')}"
                frontier.add_url(url=job_url, source_name=self.get_source_name(), priority=5, depth=1)

                posting_time = None
                if item.get("pubDate"):
                    try:
                        posting_time = datetime.fromisoformat(item["pubDate"].replace("Z", "+00:00"))
                    except Exception:
                        posting_time = datetime.utcnow()

                sal_min = None
                sal_max = None
                if item.get("annualSalaryMin"):
                    try:
                        sal_min = float(item["annualSalaryMin"])
                    except Exception:
                        pass
                if item.get("annualSalaryMax"):
                    try:
                        sal_max = float(item["annualSalaryMax"])
                    except Exception:
                        pass

                raw_desc = item.get("jobDescription") or ""
                job_record = {
                    "job_title": item.get("jobTitle", "Software Engineer"),
                    "company": item.get("companyName", "Confidential"),
                    "location_raw": item.get("jobGeo", "Remote"),
                    "city": "Remote",
                    "country": item.get("jobGeo", "Global"),
                    "is_remote": True,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "salary_currency": item.get("salaryCurrency", "USD"),
                    "salary_period": "yearly",
                    "experience_min_years": None,
                    "experience_max_years": None,
                    "experience_level": item.get("jobLevel"),
                    "description_raw": raw_desc,
                    "raw_html": raw_desc[:50000] if raw_desc else "",
                    "posting_date": posting_time or datetime.utcnow(),
                    "job_url": job_url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Extracted {len(extracted_jobs)} jobs from Jobicy", 200)

        except Exception as e:
            logger.error(f"Error parsing Jobicy API response: {e}")
            if log_callback:
                log_callback("ERROR", f"Jobicy parse error: {e}", 500)

        return extracted_jobs
