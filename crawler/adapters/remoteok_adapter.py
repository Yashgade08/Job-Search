"""
RemoteOK Permitted Remote Tech Jobs Adapter
Crawls authorized public remote engineering positions with salary data and tech tags.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapter.remoteok")


class RemoteOKAdapter(BaseCrawlerAdapter):
    def get_source_name(self) -> str:
        return "RemoteOK"

    def get_base_url(self) -> str:
        return "https://remoteok.com"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 1,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        api_url = "https://remoteok.com/api"

        if log_callback:
            log_callback("INFO", f"Connecting to RemoteOK public feed ({api_url})", 200)

        frontier.add_url(
            url=api_url,
            source_name=self.get_source_name(),
            priority=1,
            depth=0
        )

        status_code, body, meta = self.fetch_page(api_url)
        if status_code != 200 or not body:
            if log_callback:
                log_callback("WARNING", f"RemoteOK request returned status {status_code}", status_code)
            return extracted_jobs

        try:
            items = json.loads(body)
            # The first element of RemoteOK API is legal disclaimer metadata
            job_items = [it for it in items if isinstance(it, dict) and "position" in it]
            
            # Slice according to max_pages
            limit = min(len(job_items), max_pages * 25)
            job_items = job_items[:limit]

            for item in job_items:
                job_url = item.get("url") or f"{self.get_base_url()}/job/{item.get('id')}"
                frontier.add_url(
                    url=job_url,
                    source_name=self.get_source_name(),
                    priority=5,
                    depth=1
                )

                posting_time = None
                if item.get("date"):
                    try:
                        posting_time = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
                    except Exception:
                        posting_time = datetime.utcnow()

                # Salaries
                sal_min = None
                sal_max = None
                if item.get("salary_min"):
                    try:
                        sal_min = float(item["salary_min"])
                    except Exception:
                        pass
                if item.get("salary_max"):
                    try:
                        sal_max = float(item["salary_max"])
                    except Exception:
                        pass

                tags = item.get("tags") or []
                raw_desc = item.get("description") or ""
                full_desc = f"{raw_desc} \n\nTags: {', '.join(tags)}"

                job_record = {
                    "job_title": item.get("position", "Software Engineer"),
                    "company": item.get("company", "Confidential"),
                    "location_raw": item.get("location", "Worldwide Remote"),
                    "city": "Remote",
                    "country": "Worldwide",
                    "is_remote": True,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "salary_currency": "USD",
                    "salary_period": "yearly",
                    "experience_min_years": None,
                    "experience_max_years": None,
                    "experience_level": None,
                    "description_raw": full_desc,
                    "raw_html": raw_desc[:50000] if raw_desc else "",
                    "posting_date": posting_time or datetime.utcnow(),
                    "job_url": job_url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Extracted {len(extracted_jobs)} verified remote jobs from RemoteOK", 200)

        except Exception as e:
            logger.error(f"Error parsing RemoteOK data: {e}")
            if log_callback:
                log_callback("ERROR", f"RemoteOK parse error: {e}", 500)

        return extracted_jobs
