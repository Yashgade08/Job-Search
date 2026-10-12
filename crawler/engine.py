"""
Crawl Engine Orchestrator
Manages the end-to-end crawling lifecycle: Frontier Queue, Politeness, Adapter Dispatch,
NLP Processing Pipeline, Telemetry, and Database Persistence.
"""

import uuid
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from crawler.frontier import CrawlFrontier
from crawler.pipelines import pipeline
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.adapters.arbeitnow_adapter import ArbeitnowAdapter
from crawler.adapters.remoteok_adapter import RemoteOKAdapter
from crawler.adapters.jobicy_adapter import JobicyAdapter
from crawler.adapters.greenhouse_adapter import GreenhouseCareerAdapter
from crawler.adapters.portal_adapters import NaukriAdapter, IndeedAdapter, FounditAdapter
from crawler.adapters.mock_portal_adapter import MockPortalAdapter
from database.connection import session_scope
from database.repository import create_crawl_run, update_crawl_run, add_crawl_log

logger = logging.getLogger("job_crawler.engine")

ADAPTER_REGISTRY: Dict[str, type] = {
    "arbeitnow": ArbeitnowAdapter,
    "remoteok": RemoteOKAdapter,
    "jobicy": JobicyAdapter,
    "greenhouse": GreenhouseCareerAdapter,
    "naukri": NaukriAdapter,
    "indeed": IndeedAdapter,
    "foundit": FounditAdapter,
    "mock": MockPortalAdapter,
}


class CrawlEngine:
    def __init__(self):
        self.frontier = CrawlFrontier()

    def get_adapter(self, source_name: str) -> BaseCrawlerAdapter:
        source_key = source_name.lower().strip()
        adapter_cls = ADAPTER_REGISTRY.get(source_key)
        if not adapter_cls:
            # Fallback matching
            for k, cls in ADAPTER_REGISTRY.items():
                if k in source_key or source_key in k:
                    return cls()
            return ArbeitnowAdapter()
        return adapter_cls()

    def execute_crawl(
        self,
        source_name: str = "arbeitnow",
        max_pages: int = 3,
        query: str = "",
        run_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a crawl run with live telemetry and database persistence.
        """
        run_uuid = run_uuid or str(uuid.uuid4())[:12]
        adapter = self.get_adapter(source_name)
        canonical_source = adapter.get_source_name()

        logger.info(f"Initiating crawl run {run_uuid} for source: {canonical_source}")

        # 1. Initialize Crawl Run in Database
        with session_scope() as sess:
            db_run = create_crawl_run(sess, run_uuid=run_uuid, source_name=canonical_source)
            run_id = db_run.id

        start_time = time.time()
        discovered_urls_count = 0
        pages_crawled_count = 0
        jobs_extracted_count = 0
        duplicates_count = 0
        errors_count = 0
        http_200_count = 0
        http_429_count = 0
        http_other_count = 0

        def log_audit(level: str, message: str, status_code: Optional[int] = None):
            nonlocal http_200_count, http_429_count, http_other_count, errors_count
            if status_code == 200:
                http_200_count += 1
            elif status_code == 429:
                http_429_count += 1
                errors_count += 1
            elif status_code and status_code >= 400:
                http_other_count += 1
                errors_count += 1

            with session_scope() as sess:
                add_crawl_log(
                    sess,
                    run_id=run_id,
                    level=level,
                    message=message,
                    status_code=status_code
                )

        try:
            log_audit("INFO", f"Engine started crawling {canonical_source} with max_pages={max_pages}", 200)

            # 2. Run Adapter Crawl & URL Discovery
            raw_items = adapter.crawl(
                frontier=self.frontier,
                max_pages=max_pages,
                query=query,
                log_callback=log_audit
            )

            discovered_urls_count = self.frontier.total_discovered
            pages_crawled_count = max_pages

            # 3. Process extracted jobs through pipeline
            for item in raw_items:
                item["crawl_run_id"] = run_id
                with session_scope() as sess:
                    status, result = pipeline.process_item(item, session=sess)
                    if status == "saved":
                        jobs_extracted_count += 1
                    elif status == "duplicate":
                        duplicates_count += 1
                    else:
                        errors_count += 1

            elapsed = max(0.1, time.time() - start_time)
            avg_page_ms = round((elapsed / max(1, pages_crawled_count)) * 1000, 1)

            # 4. Finalize Crawl Run
            with session_scope() as sess:
                update_crawl_run(
                    sess,
                    run_id=run_id,
                    status="completed",
                    urls_discovered=discovered_urls_count,
                    pages_crawled=pages_crawled_count,
                    jobs_extracted=jobs_extracted_count,
                    duplicates_skipped=duplicates_count,
                    errors_count=errors_count,
                    duration_seconds=round(elapsed, 2),
                    average_page_time_ms=avg_page_ms,
                    http_200_count=http_200_count,
                    http_429_count=http_429_count,
                    http_other_count=http_other_count
                )

            log_audit("INFO", f"Crawl run completed! Saved: {jobs_extracted_count}, Duplicates: {duplicates_count}", 200)

            return {
                "run_id": run_id,
                "run_uuid": run_uuid,
                "status": "completed",
                "source": canonical_source,
                "duration_seconds": round(elapsed, 2),
                "urls_discovered": discovered_urls_count,
                "jobs_extracted": jobs_extracted_count,
                "duplicates_skipped": duplicates_count,
                "errors_count": errors_count,
            }

        except Exception as e:
            elapsed = max(0.1, time.time() - start_time)
            logger.error(f"Fatal crawl error in run {run_uuid}: {e}", exc_info=True)
            log_audit("ERROR", f"Crawl interrupted: {e}", 500)
            with session_scope() as sess:
                update_crawl_run(
                    sess,
                    run_id=run_id,
                    status="failed",
                    errors_count=errors_count + 1,
                    duration_seconds=round(elapsed, 2),
                    error_summary=str(e)
                )
            return {
                "run_id": run_id,
                "run_uuid": run_uuid,
                "status": "failed",
                "error": str(e)
            }


crawl_engine = CrawlEngine()
