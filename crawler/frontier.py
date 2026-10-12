"""
Crawl Frontier and URL Discovery Queue Engine
Manages crawl prioritization, depth traversal, canonical URL normalization,
and visited set filtering.
"""

import heapq
import time
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Dict, Any, Optional, Tuple, Set, List


# Query parameters commonly used for tracking, analytics, and session IDs to strip
TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "ref", "reference", "source", "session_id",
    "spm", "tracking_id", "trk", "trkinfo", "originalsubdomain",
    "_ga", "mc_cid", "mc_eid", "campaign_id"
}


def normalize_canonical_url(url: str) -> str:
    """
    Standardizes URL to a canonical format:
    - Lowercases scheme and netloc
    - Strips fragment (#...)
    - Strips tracking/analytics query parameters
    - Alphabetically sorts remaining query parameters
    - Normalizes path slashes
    """
    if not url or not url.strip():
        return ""

    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Default to https if no scheme
    if not scheme:
        scheme = "https"

    path = parsed.path
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Clean query parameters
    query_params = parse_qsl(parsed.query, keep_blank_values=False)
    filtered_params = [
        (k, v) for k, v in query_params if k.lower() not in TRACKING_QUERY_PARAMS
    ]
    filtered_params.sort(key=lambda x: x[0])
    clean_query = urlencode(filtered_params)

    # Reconstruct
    canonical = urlunparse((scheme, netloc, path, "", clean_query, ""))
    return canonical


class FrontierItem:
    """Item placed in priority queue with min-heap ordering."""
    def __init__(self, priority: int, depth: int, url: str, canonical_url: str, source_name: str, meta: Optional[Dict] = None):
        self.priority = priority  # Lower number = higher priority
        self.depth = depth
        self.url = url
        self.canonical_url = canonical_url
        self.source_name = source_name
        self.meta = meta or {}
        self.discovered_at = time.time()

    def __lt__(self, other: "FrontierItem") -> bool:
        if self.priority != other.priority:
            return self.priority < other.priority
        if self.depth != other.depth:
            return self.depth < other.depth
        return self.discovered_at < other.discovered_at


class CrawlFrontier:
    """
    In-memory Priority Frontier with Domain Queues and Visited Filter.
    Can sync state with PostgreSQL/SQLite.
    """
    def __init__(self):
        self._queue: List[FrontierItem] = []
        self._visited_urls: Set[str] = set()
        self._enqueued_urls: Set[str] = set()
        
        # Telemetry
        self.total_discovered = 0
        self.total_crawled = 0
        self.total_skipped = 0
        self.total_failed = 0

    def add_url(
        self,
        url: str,
        source_name: str,
        priority: int = 10,
        depth: int = 0,
        meta: Optional[Dict] = None
    ) -> bool:
        """
        Adds a URL to the frontier if it hasn't been crawled or enqueued.
        Returns True if newly added, False if duplicate.
        """
        canonical = normalize_canonical_url(url)
        if not canonical:
            return False

        if canonical in self._visited_urls or canonical in self._enqueued_urls:
            self.total_skipped += 1
            return False

        item = FrontierItem(
            priority=priority,
            depth=depth,
            url=url,
            canonical_url=canonical,
            source_name=source_name,
            meta=meta
        )
        heapq.heappush(self._queue, item)
        self._enqueued_urls.add(canonical)
        self.total_discovered += 1
        return True

    def get_next(self) -> Optional[FrontierItem]:
        """Pops highest-priority item from queue."""
        while self._queue:
            item = heapq.heappop(self._queue)
            if item.canonical_url in self._visited_urls:
                continue
            self._enqueued_urls.discard(item.canonical_url)
            self._visited_urls.add(item.canonical_url)
            self.total_crawled += 1
            return item
        return None

    def mark_failed(self, item: FrontierItem):
        """Records a crawl failure."""
        self.total_failed += 1

    def is_visited(self, url: str) -> bool:
        return normalize_canonical_url(url) in self._visited_urls

    def size(self) -> int:
        return len(self._queue)

    def stats(self) -> Dict[str, Any]:
        return {
            "queue_size": len(self._queue),
            "discovered": self.total_discovered,
            "crawled": self.total_crawled,
            "skipped_duplicates": self.total_skipped,
            "failed": self.total_failed,
        }
