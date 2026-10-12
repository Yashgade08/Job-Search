"""
Scrapy Career Spider
Demonstrates full Scrapy framework architecture for URL discovery, link extraction,
pagination following, and job item yield.
"""

import scrapy
from typing import Iterator
from bs4 import BeautifulSoup


class JobMarketSpider(scrapy.Spider):
    name = "job_market_spider"
    allowed_domains = ["arbeitnow.com", "remoteok.com", "github.com"]
    start_urls = [
        "https://www.arbeitnow.com/jobs",
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2.0,
    }

    def parse(self, response: scrapy.http.Response) -> Iterator[scrapy.Request]:
        # 1. URL Discovery: Extract job detail page links
        job_links = response.css("a[href*='/jobs/']::attr(href)").getall()
        for link in job_links:
            full_url = response.urljoin(link)
            if "/jobs/" in full_url and not full_url.endswith("/jobs"):
                yield response.follow(full_url, callback=self.parse_job_detail)

        # 2. Pagination: Follow next page if within limits
        next_page = response.css("a[rel='next']::attr(href), a:contains('Next')::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_job_detail(self, response: scrapy.http.Response):
        # Extract job metadata
        soup = BeautifulSoup(response.text, "html.parser")
        title = response.css("h1::text").get() or soup.title.string if soup.title else "Software Engineer"
        company = response.css("[class*='company']::text, h2::text").get() or "Confidential"
        desc = response.css("div[itemprop='description'], .job-description, article").get() or response.text

        yield {
            "job_title": title.strip(),
            "company": company.strip(),
            "job_url": response.url,
            "description_raw": desc,
            "source_portal": "ScrapyCareerSpider",
            "raw_html": response.text[:40000],
        }
