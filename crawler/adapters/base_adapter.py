"""
Abstract Base Crawler Adapter
Defines the standard interface for source-specific crawl adapters,
integrating robots.txt compliance, polite rate limiting, retries, and telemetry.
"""

import abc
import time
import logging
from typing import Dict, Any, Optional, List, Tuple, Callable
import requests
from config.settings import settings
from crawler.politeness import robots_checker, rate_limiter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapter")


class BaseCrawlerAdapter(abc.ABC):
    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or settings.default_user_agent
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    @abc.abstractmethod
    def get_source_name(self) -> str:
        """Unique identifier of the job source / portal."""
        pass

    @abc.abstractmethod
    def get_base_url(self) -> str:
        """Base domain URL for the source."""
        pass

    def verify_compliance(self, url: str) -> Tuple[bool, str]:
        """
        Verifies robots.txt and access restrictions before making any HTTP request.
        Returns: (is_allowed: bool, reason: str)
        """
        if not settings.obey_robots_txt:
            return True, "Robots.txt check disabled in configuration."

        try:
            allowed = robots_checker.is_allowed(url)
            if not allowed:
                return False, f"URL path is forbidden by robots.txt directives for {self.get_source_name()}."
            return True, "Robots.txt check passed."
        except Exception as e:
            return True, f"Robots.txt check warning: {e}; proceeding with default polite delay."

    def fetch_page(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[int, str, Dict[str, Any]]:
        """
        Performs a polite, rate-limited HTTP request with retries and circuit breaker.
        Returns: (status_code, response_text, telemetry_dict)
        """
        # 1. Compliance verification
        allowed, reason = self.verify_compliance(url)
        if not allowed:
            logger.warning(f"Aborting request to {url}: {reason}")
            return 403, "", {"error": reason, "blocked_by_robots_txt": True}

        # 2. Enforce polite rate limit delay
        try:
            rate_limiter.wait_polite_delay(url, robots_checker)
        except RuntimeError as e:
            logger.error(str(e))
            return 429, "", {"error": str(e), "circuit_breaker_open": True}

        req_timeout = timeout or settings.request_timeout_seconds
        req_headers = headers or {}
        attempts = 0
        max_attempts = settings.max_retries

        while attempts < max_attempts:
            attempts += 1
            start_t = time.time()
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=req_headers,
                    timeout=req_timeout,
                )
                elapsed_ms = round((time.time() - start_t) * 1000, 1)

                if resp.status_code == 200:
                    rate_limiter.record_success(url)
                    return resp.status_code, resp.text, {
                        "elapsed_ms": elapsed_ms,
                        "attempts": attempts,
                        "content_type": resp.headers.get("Content-Type", ""),
                    }
                elif resp.status_code == 429 or resp.status_code >= 500:
                    rate_limiter.record_rate_limited_or_error(url, resp.status_code)
                    logger.warning(f"Received status {resp.status_code} on {url}. Retry {attempts}/{max_attempts}...")
                    time.sleep(settings.backoff_factor ** attempts)
                else:
                    # Client errors (400, 404, etc.)
                    return resp.status_code, resp.text, {"elapsed_ms": elapsed_ms, "attempts": attempts}

            except requests.RequestException as e:
                logger.warning(f"Request exception on {url} ({e}). Attempt {attempts}/{max_attempts}")
                time.sleep(settings.backoff_factor ** attempts)

        return 500, "", {"error": "Exceeded maximum retry attempts", "attempts": attempts}

    @abc.abstractmethod
    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 10,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes URL discovery and job item extraction.
        Returns a list of raw job dictionaries.
        """
        pass
