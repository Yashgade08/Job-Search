"""
Crawler Politeness, Robots.txt Compliance, and Rate Limiting Engine
Ensures ethical web crawling adhering strictly to robots.txt, domain crawl delays,
exponential backoff, and circuit breakers.
"""

import time
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import urllib.request
from typing import Dict, Any, Optional, Tuple
from config.settings import settings

logger = logging.getLogger("job_crawler.politeness")


class RobotsChecker:
    """
    Fetches, parses, and caches robots.txt files per domain.
    Never requests pages forbidden by robots.txt directives.
    """
    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or settings.default_user_agent
        self._parsers: Dict[str, RobotFileParser] = {}
        self._crawl_delays: Dict[str, float] = {}

    def _get_domain_root(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_parser(self, url: str) -> Optional[RobotFileParser]:
        domain_root = self._get_domain_root(url)
        if domain_root in self._parsers:
            return self._parsers[domain_root]

        robots_url = f"{domain_root}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            req = urllib.request.Request(
                robots_url,
                headers={"User-Agent": self.user_agent}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                content = response.read().decode("utf-8", errors="ignore")
                parser.parse(content.splitlines())
                
                # Check for crawl-delay directive
                delay = parser.crawl_delay(self.user_agent)
                if delay:
                    self._crawl_delays[domain_root] = float(delay)
                    logger.info(f"Respecting robots.txt Crawl-delay of {delay}s for {domain_root}")
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt for {domain_root} ({e}); defaulting to polite crawl.")
            # Create a permissive parser if robots.txt returns 404 or cannot be reached
            parser.allow_all = True

        self._parsers[domain_root] = parser
        return parser

    def is_allowed(self, url: str) -> bool:
        """
        Returns True if the URL is allowed for crawling by robots.txt.
        Never bypasses robots.txt restrictions.
        """
        if not settings.obey_robots_txt:
            return True

        domain_root = self._get_domain_root(url)
        parser = self.get_parser(url)
        if not parser:
            return True

        allowed = parser.can_fetch(self.user_agent, url)
        if not allowed:
            logger.warning(f"Crawling forbidden by robots.txt: {url}")
        return allowed

    def get_crawl_delay(self, url: str) -> float:
        domain_root = self._get_domain_root(url)
        return self._crawl_delays.get(domain_root, settings.default_download_delay_seconds)


class RateLimiter:
    """
    Enforces per-domain polite crawl delays, exponential backoff on 429/503,
    and circuit breaker states.
    """
    def __init__(self):
        self._last_request_time: Dict[str, float] = {}
        self._consecutive_errors: Dict[str, int] = {}
        self._circuit_open_until: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    def is_circuit_open(self, url: str) -> Tuple[bool, float]:
        """Checks if circuit breaker has tripped for this domain."""
        domain = self._get_domain(url)
        open_until = self._circuit_open_until.get(domain, 0)
        now = time.time()
        if now < open_until:
            remaining = round(open_until - now, 1)
            return True, remaining
        return False, 0.0

    def wait_polite_delay(self, url: str, robots_checker: RobotsChecker):
        """
        Sleeps if necessary to respect the domain's minimum polite crawl interval.
        """
        domain = self._get_domain(url)
        now = time.time()

        # Check circuit breaker
        circuit_open, remaining = self.is_circuit_open(url)
        if circuit_open:
            raise RuntimeError(f"Circuit breaker open for {domain} due to repeated rate limits. Cooldown: {remaining}s")

        # Determine delay
        domain_delay = robots_checker.get_crawl_delay(url)
        domain_delay = max(domain_delay, settings.default_download_delay_seconds)

        # Backoff multiplier if consecutive errors occurred
        consecutive = self._consecutive_errors.get(domain, 0)
        if consecutive > 0:
            domain_delay = min(
                settings.max_download_delay_seconds,
                domain_delay * (settings.backoff_factor ** consecutive)
            )

        last_time = self._last_request_time.get(domain, 0)
        elapsed = now - last_time
        if elapsed < domain_delay:
            sleep_needed = domain_delay - elapsed
            time.sleep(sleep_needed)

        self._last_request_time[domain] = time.time()

    def record_success(self, url: str):
        domain = self._get_domain(url)
        self._consecutive_errors[domain] = 0

    def record_rate_limited_or_error(self, url: str, status_code: int):
        domain = self._get_domain(url)
        current = self._consecutive_errors.get(domain, 0) + 1
        self._consecutive_errors[domain] = current

        # If domain hits 4 consecutive 429s or 503s, trip circuit breaker for 60 seconds
        if current >= 4:
            cooldown_seconds = 60.0
            self._circuit_open_until[domain] = time.time() + cooldown_seconds
            logger.warning(
                f"Tripped circuit breaker for {domain}! Received {current} rate limit errors. Pausing domain for {cooldown_seconds}s."
            )


# Singleton instances
robots_checker = RobotsChecker()
rate_limiter = RateLimiter()
