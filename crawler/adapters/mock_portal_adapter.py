"""
Mock Live Portal Adapter for Deterministic Testing and Verification
Simulates multi-page pagination, rate limits, duplicate listings, and diverse tech jobs.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

# Realistic synthetic job dataset designed to test extraction of India tech roles:
# VLSI Engineers, Consultants, and SDE/SWE
MOCK_DATABASE = [
    {
        "page": 1,
        "title": "Senior VLSI Physical Design Engineer",
        "company": "Qualcomm India",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 2400000,
        "salary_max": 3800000,
        "desc": """
        Qualcomm India is hiring a Senior VLSI Physical Design Engineer for cutting-edge mobile 4nm SoCs.
        Requirements:
        - 4+ years of hands-on experience in VLSI Physical Design, P&R, and floorplanning.
        - Expertise in Static Timing Analysis (STA), Primetime, and timing closure.
        - Proficiency in Cadence Tools (Innovus) or Synopsys Tools (ICC2, Fusion Compiler).
        - Solid knowledge of CMOS, FinFET technology, and Low Power Design.
        - Scripting skills in Python or TCL.
        - Excellent Problem Solving and Team Collaboration.
        Nice to have:
        - Exposure to SystemVerilog, Verilog, and RTL synthesis.
        """
    },
    {
        "page": 1,
        "title": "Senior Technology Consultant - Digital & Cloud",
        "company": "Deloitte India",
        "location": "Hyderabad, India",
        "is_remote": False,
        "salary_min": 1800000,
        "salary_max": 3200000,
        "desc": """
        Join Deloitte's Technology Advisory practice as a Senior Consultant.
        Qualifications:
        - 5+ years of experience in Technology Consulting, IT Strategy, and Digital Transformation.
        - Strong background in Solution Architecture and enterprise cloud migration on AWS or Azure.
        - Experience in Business Analysis, BRD documentation, and requirement gathering.
        - Familiarity with ERP & SAP systems, Microservices, and API integration.
        - Exceptional Stakeholder Management, Client Advisory, and presentation skills.
        Bonus points:
        - Agile / Scrum certification and Financial Modeling experience.
        """
    },
    {
        "page": 1,
        "title": "Software Development Engineer II (SDE 2)",
        "company": "Amazon India",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 2800000,
        "salary_max": 4600000,
        "desc": """
        Amazon Prime Video team in Bengaluru is seeking an SDE 2 to build high-scale distributed systems.
        Requirements:
        - 3+ years of experience as an SDE or Software Engineer in Java, Go, or C++.
        - Mastery of Data Structures & Algorithms (DSA), System Design, and Object-Oriented Design.
        - Hands-on experience building scalable Microservices, REST APIs, and event-driven architectures with Kafka.
        - Experience with AWS (EC2, S3, DynamoDB), Docker, and Redis caching.
        - Unit Testing with pytest or JUnit, and CI/CD automation with GitHub Actions.
        - Strong Ownership and customer obsession.
        """
    },
    {
        "page": 2,
        "title": "Staff ASIC Verification Engineer (UVM & SystemVerilog)",
        "company": "Intel India",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 3200000,
        "salary_max": 5200000,
        "desc": """
        Lead silicon pre-silicon verification for high-performance server processors.
        Requirements:
        - 6+ years of pre-silicon verification using SystemVerilog and UVM methodology.
        - Deep expertise in RTL Design, Computer Architecture, and PCIe / AXI bus protocols.
        - Experience with ModelSim / Questa, VCS, and coverage-driven verification.
        - Scripting in Python and Bash for automated regressions.
        - Leadership, technical mentorship, and cross-functional collaboration.
        Nice to have:
        - Formal verification and DFT knowledge.
        """
    },
    {
        "page": 2,
        "title": "Associate Management Consultant - Tech Strategy",
        "company": "McKinsey & Company",
        "location": "Gurgaon, India",
        "is_remote": False,
        "salary_min": 2500000,
        "salary_max": 4200000,
        "desc": """
        Shape CXO agendas and digital transformation strategies across India and APAC.
        Requirements:
        - 3+ years of experience in Management Consulting, Strategic Advisory, or Tech Consulting.
        - Strong capabilities in Business Analysis, Market Intelligence, and Financial Modeling.
        - Client Advisory, executive presentation, and cross-functional alignment.
        - Structured Problem Solving and analytical frameworks.
        - Degree in Engineering or MBA from a premier institution.
        """
    },
    {
        "page": 2,
        # INTENTIONAL DUPLICATE to test Deduplication Engine!
        "title": "Senior VLSI Physical Design Engineer",
        "company": "Qualcomm India",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 2400000,
        "salary_max": 3800000,
        "desc": """
        Qualcomm India is hiring a Senior VLSI Physical Design Engineer for cutting-edge mobile 4nm SoCs.
        Requirements:
        - 4+ years of hands-on experience in VLSI Physical Design, P&R, and floorplanning.
        """
    },
]


class MockPortalAdapter(BaseCrawlerAdapter):
    """
    Simulates a live multi-page portal for unit tests and local benchmarking.
    """
    def get_source_name(self) -> str:
        return "MockPortal"

    def get_base_url(self) -> str:
        return "http://mock-jobs.local"

    def crawl(
        self,
        frontier: CrawlFrontier,
        max_pages: int = 2,
        query: str = "",
        log_callback: Optional[Callable[[str, str, Optional[int]], None]] = None
    ) -> List[Dict[str, Any]]:
        extracted_jobs = []

        for page in range(1, max_pages + 1):
            page_url = f"{self.get_base_url()}/jobs?page={page}"
            if log_callback:
                log_callback("INFO", f"Mock adapter scanning page {page} ({page_url})", 200)

            frontier.add_url(url=page_url, source_name=self.get_source_name(), priority=1, depth=0)

            # Retrieve jobs for this mock page
            page_jobs = [j for j in MOCK_DATABASE if j["page"] == page]
            if not page_jobs:
                break

            for idx, raw in enumerate(page_jobs):
                job_url = f"{self.get_base_url()}/job/{page}-{idx}-{raw['title'].replace(' ', '-').lower()}"
                frontier.add_url(url=job_url, source_name=self.get_source_name(), priority=5, depth=1)

                job_record = {
                    "job_title": raw["title"],
                    "company": raw["company"],
                    "location_raw": raw["location"],
                    "city": raw["location"].split(",")[0].strip(),
                    "country": "India" if "India" in raw["location"] else ("USA" if "NY" in raw["location"] or "CA" in raw["location"] else "Europe"),
                    "is_remote": raw["is_remote"],
                    "salary_min": raw["salary_min"],
                    "salary_max": raw["salary_max"],
                    "salary_currency": "USD",
                    "salary_period": "yearly",
                    "description_raw": raw["desc"],
                    "description_cleaned": raw["desc"],
                    "raw_html": f"<html><body><h1>{raw['title']}</h1><p>{raw['desc']}</p></body></html>",
                    "posting_date": datetime.utcnow() - timedelta(days=idx),
                    "job_url": job_url,
                    "source_portal": self.get_source_name(),
                }
                extracted_jobs.append(job_record)

            if log_callback:
                log_callback("INFO", f"Mock adapter emitted {len(page_jobs)} items from page {page}", 200)

        return extracted_jobs
