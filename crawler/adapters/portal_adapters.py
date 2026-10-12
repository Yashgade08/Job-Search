"""
Ethical Job Portal Crawler Adapters (Naukri, Indeed, Foundit, Glassdoor)
Implements domain-specific BeautifulSoup parsers, strict robots.txt verification,
polite crawl delays, and zero-bypass anti-bot compliance.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

logger = logging.getLogger("job_crawler.adapters.portals")


class NaukriAdapter(BaseCrawlerAdapter):
    """
    Naukri.com Crawler Adapter.
    Verifies robots.txt and terms. Never bypasses anti-bot or CAPTCHA challenges.
    """
    def get_source_name(self) -> str:
        return "Naukri"

    def get_base_url(self) -> str:
        return "https://www.naukri.com"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 1,
        query: str = "software-engineer",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        clean_query = quote_plus(query or "software-developer")
        search_url = f"{self.get_base_url()}/{clean_query}-jobs"

        if log_callback:
            log_callback("INFO", f"Auditing robots.txt and crawling compliance for Naukri ({search_url})", 200)

        # 1. Compliance verification
        allowed, reason = self.verify_compliance(search_url)
        if not allowed:
            if log_callback:
                log_callback("WARNING", f"Naukri robots.txt check: {reason}. Ethical crawler halting.", 403)
            return extracted_jobs

        frontier.add_url(url=search_url, source_name=self.get_source_name(), priority=1, depth=0)

        # 2. Polite request
        status_code, html_content, meta = self.fetch_page(search_url)
        if status_code != 200 or not html_content:
            if log_callback:
                log_callback(
                    "WARNING",
                    f"Naukri returned status {status_code}. Anti-bot/Cloudflare detected; bypassing is strictly prohibited.",
                    status_code
                )
            return extracted_jobs

        # 3. Domain-specific BeautifulSoup Parsing
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            job_cards = soup.select(".srp-jobtuple-wrapper, .cust-job-tuple, .jobTuple")
            
            for card in job_cards[:max_pages * 15]:
                title_elem = card.select_one(".title, .job-title, a[class*='title']")
                company_elem = card.select_one(".comp-name, .company-name, a[class*='company']")
                location_elem = card.select_one(".loc-wrap, .location, span[class*='loc']")
                exp_elem = card.select_one(".exp-wrap, .experience, span[class*='exp']")
                sal_elem = card.select_one(".sal-wrap, .salary, span[class*='sal']")
                desc_elem = card.select_one(".job-desc, .desc, .tags-container")
                url_elem = card.select_one("a[href*='job-listings']")

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True) if company_elem else "Confidential"
                location = location_elem.get_text(strip=True) if location_elem else "India"
                experience = exp_elem.get_text(strip=True) if exp_elem else ""
                salary = sal_elem.get_text(strip=True) if sal_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else f"Job posting for {title} at {company}."
                job_url = url_elem["href"] if url_elem and url_elem.has_attr("href") else search_url

                frontier.add_url(url=job_url, source_name=self.get_source_name(), priority=5, depth=1)

                job_record = {
                    "job_title": title,
                    "company": company,
                    "location_raw": location,
                    "city": location.split(",")[0].strip(),
                    "country": "India",
                    "is_remote": "remote" in location.lower(),
                    "salary_min": None,
                    "salary_max": None,
                    "salary_currency": "INR",
                    "salary_period": "yearly",
                    "description_raw": f"{desc} | Experience: {experience} | Salary: {salary}",
                    "job_url": job_url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Naukri adapter extracted {len(extracted_jobs)} job postings", 200)

        except Exception as e:
            logger.error(f"Naukri parsing error: {e}")
            if log_callback:
                log_callback("ERROR", f"Naukri parse error: {e}", 500)

        return extracted_jobs


class IndeedAdapter(BaseCrawlerAdapter):
    """
    Indeed Crawler Adapter.
    Adheres strictly to robots.txt and domain rate limits.
    """
    def get_source_name(self) -> str:
        return "Indeed"

    def get_base_url(self) -> str:
        return "https://www.indeed.com"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 1,
        query: str = "python developer",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        clean_q = quote_plus(query or "software engineer")
        search_url = f"{self.get_base_url()}/jobs?q={clean_q}&l="

        if log_callback:
            log_callback("INFO", f"Checking Indeed robots.txt and compliance ({search_url})", 200)

        allowed, reason = self.verify_compliance(search_url)
        if not allowed:
            if log_callback:
                log_callback("WARNING", f"Indeed robots.txt directive forbids crawling: {reason}", 403)
            return extracted_jobs

        frontier.add_url(url=search_url, source_name=self.get_source_name(), priority=1, depth=0)

        status_code, html_content, meta = self.fetch_page(search_url)
        if status_code != 200 or not html_content:
            if log_callback:
                log_callback("WARNING", f"Indeed returned status {status_code} (anti-bot protection active).", status_code)
            return extracted_jobs

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            job_cards = soup.select(".job_seen_beacon, .result, .tapItem")

            for card in job_cards[:max_pages * 15]:
                title_elem = card.select_one("h2.jobTitle, .jcs-JobTitle")
                comp_elem = card.select_one("[data-testid='company-name'], .companyName")
                loc_elem = card.select_one("[data-testid='text-location'], .companyLocation")
                sal_elem = card.select_one("[data-testid='attribute_snippet_salary'], .salary-snippet-container")
                desc_elem = card.select_one(".job-snippet, .underShelfFooter")
                link_elem = card.select_one("a[id*='job_'], a[class*='jcs-JobTitle']")

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                comp = comp_elem.get_text(strip=True) if comp_elem else "Confidential"
                loc = loc_elem.get_text(strip=True) if loc_elem else "United States"
                sal = sal_elem.get_text(strip=True) if sal_elem else ""
                desc = desc_elem.get_text(strip=True) if desc_elem else ""
                href = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
                job_url = f"{self.get_base_url()}{href}" if href.startswith("/") else (href or search_url)

                frontier.add_url(url=job_url, source_name=self.get_source_name(), priority=5, depth=1)

                job_record = {
                    "job_title": title,
                    "company": comp,
                    "location_raw": loc,
                    "city": loc.split(",")[0].strip(),
                    "country": "United States",
                    "is_remote": "remote" in loc.lower(),
                    "salary_min": None,
                    "salary_max": None,
                    "salary_currency": "USD",
                    "salary_period": "yearly",
                    "description_raw": f"{desc} | Compensation: {sal}",
                    "job_url": job_url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Indeed adapter parsed {len(extracted_jobs)} jobs", 200)

        except Exception as e:
            logger.error(f"Indeed parse exception: {e}")

        return extracted_jobs


class FounditAdapter(BaseCrawlerAdapter):
    """
    Foundit (formerly Monster) Crawler Adapter.
    """
    def get_source_name(self) -> str:
        return "Foundit"

    def get_base_url(self) -> str:
        return "https://www.foundit.in"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 1,
        query: str = "software engineer",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []
        clean_q = quote_plus(query or "software-engineer")
        search_url = f"{self.get_base_url()}/srp/results?query={clean_q}"

        if log_callback:
            log_callback("INFO", f"Checking Foundit robots.txt compliance ({search_url})", 200)

        allowed, reason = self.verify_compliance(search_url)
        if not allowed:
            if log_callback:
                log_callback("WARNING", f"Foundit crawl restricted by robots.txt: {reason}", 403)
            return extracted_jobs

        frontier.add_url(url=search_url, source_name=self.get_source_name(), priority=1, depth=0)
        status_code, html, meta = self.fetch_page(search_url)
        if status_code != 200 or not html:
            if log_callback:
                log_callback("WARNING", f"Foundit returned {status_code} (anti-bot protection)", status_code)
            return extracted_jobs

        try:
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".srpResultCard, .job-card")
            for card in cards[:max_pages * 15]:
                title_elem = card.select_one(".jobTitle, .title")
                comp_elem = card.select_one(".companyName, .company")
                loc_elem = card.select_one(".location, .loc")
                desc_elem = card.select_one(".jobDesc, .desc")
                url_elem = card.select_one("a[href*='job']")

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                comp = comp_elem.get_text(strip=True) if comp_elem else "Confidential"
                loc = loc_elem.get_text(strip=True) if loc_elem else "India"
                desc = desc_elem.get_text(strip=True) if desc_elem else ""
                url = url_elem["href"] if url_elem and url_elem.has_attr("href") else search_url

                job_record = {
                    "job_title": title,
                    "company": comp,
                    "location_raw": loc,
                    "city": loc.split(",")[0].strip(),
                    "country": "India",
                    "is_remote": "remote" in loc.lower(),
                    "salary_min": None,
                    "salary_max": None,
                    "salary_currency": "INR",
                    "salary_period": "yearly",
                    "description_raw": desc,
                    "job_url": url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Foundit adapter extracted {len(extracted_jobs)} jobs", 200)

        except Exception as e:
            logger.error(f"Foundit parse error: {e}")

        return extracted_jobs
