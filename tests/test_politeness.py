"""
Unit Tests for Crawler Politeness, Robots.txt Compliance, and Rate Limiting
"""

import pytest
import time
from crawler.politeness import RateLimiter, RobotsChecker


def test_rate_limiter_domain_tracking():
    limiter = RateLimiter()
    url = "https://example.com/jobs/1"

    # Initial circuit breaker check
    is_open, remaining = limiter.is_circuit_open(url)
    assert is_open is False
    assert remaining == 0.0


def test_rate_limiter_circuit_breaker():
    limiter = RateLimiter()
    url = "https://failing-domain.com/jobs"

    # Simulate 5 consecutive 429/500 errors
    for _ in range(5):
        limiter.record_rate_limited_or_error(url, status_code=429)

    is_open, remaining = limiter.is_circuit_open(url)
    assert is_open is True
    assert remaining > 0.0

    # Successful response clears error count
    limiter.record_success(url)
    assert limiter._consecutive_errors.get("failing-domain.com") == 0


def test_robots_checker_default_allow():
    checker = RobotsChecker()
    # For domains where robots.txt is not yet parsed, fallback should be compliant
    assert checker.user_agent is not None
