"""
Scrapy Crawler Settings
Configures robots.txt compliance, polite download delays, and autothrottling.
"""

from config.settings import settings

BOT_NAME = "job_demand_crawler"

SPIDER_MODULES = ["crawler.scrapy_spiders"]
NEWSPIDER_MODULE = "crawler.scrapy_spiders"

# Politeness & Robots.txt Compliance
ROBOTSTXT_OBEY = settings.obey_robots_txt
USER_AGENT = settings.default_user_agent

# Rate Limiting & Concurrency
DOWNLOAD_DELAY = settings.default_download_delay_seconds
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = settings.max_concurrent_requests_per_domain

# AutoThrottle Extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# HTTP Cache & Retries
RETRY_ENABLED = True
RETRY_TIMES = settings.max_retries
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging
LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
