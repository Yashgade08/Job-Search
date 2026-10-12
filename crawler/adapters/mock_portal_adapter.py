"""
Mock Live Portal Adapter for Deterministic Testing and Verification
Simulates multi-page pagination, rate limits, duplicate listings, and diverse tech jobs.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from crawler.adapters.base_adapter import BaseCrawlerAdapter
from crawler.frontier import CrawlFrontier

# Realistic synthetic job dataset designed to test extraction of all 7 skill categories
MOCK_DATABASE = [
    {
        "page": 1,
        "title": "Senior Backend Engineer (Python & Cloud)",
        "company": "Nexus Technologies",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 140000,
        "salary_max": 180000,
        "desc": """
        We are seeking a Senior Backend Engineer to build scalable microservices.
        Requirements:
        - 5+ years of software engineering experience with Python and FastAPI or Django.
        - Deep hands-on expertise with PostgreSQL, Redis, and Kafka event streaming.
        - Experience with Docker, Kubernetes, and AWS (EC2, S3, RDS).
        - Strong foundation in System Design, Microservices, and REST APIs.
        - Excellent Problem Solving and Team Collaboration.
        Nice to have:
        - Exposure to Go, Terraform, and GraphQL.
        """
    },
    {
        "page": 1,
        "title": "Full Stack Developer (React & Node.js)",
        "company": "Orbit Labs",
        "location": "San Francisco, CA",
        "is_remote": True,
        "salary_min": 130000,
        "salary_max": 170000,
        "desc": """
        Orbit Labs is building the next generation collaborative platform.
        Qualifications:
        - Proficient in TypeScript, JavaScript, React, and Next.js.
        - Backend experience with Node.js, Express, and PostgreSQL.
        - Experience with Tailwind CSS, HTML5, and CSS3.
        - CI/CD automation with GitHub Actions.
        - Strong communication and ownership.
        Bonus points:
        - Experience with Python, Docker, and AWS.
        """
    },
    {
        "page": 1,
        "title": "Staff Machine Learning Engineer (LLMs & RAG)",
        "company": "Cognitive AI",
        "location": "New York, NY",
        "is_remote": True,
        "salary_min": 190000,
        "salary_max": 250000,
        "desc": """
        Lead our Generative AI infrastructure and production RAG pipelines.
        Requirements:
        - 7+ years of experience with Python, PyTorch, and Machine Learning.
        - Deep expertise in LLMs, LangChain, Hugging Face, and Vector Databases (Pinecone, ChromaDB).
        - Familiarity with NLP, Deep Learning, and model fine-tuning.
        - Deployment with Docker, Kubernetes, and AWS or GCP.
        - High degree of mentorship and technical leadership.
        """
    },
    {
        "page": 2,
        "title": "DevOps & Site Reliability Engineer (SRE)",
        "company": "CloudScale Systems",
        "location": "Berlin, Germany",
        "is_remote": True,
        "salary_min": 95000,
        "salary_max": 130000,
        "desc": """
        Manage cloud infrastructure and 99.99% uptime across multi-region clusters.
        Requirements:
        - Extensive experience with Kubernetes, Docker, and Linux administration.
        - Infrastructure as Code using Terraform and Ansible.
        - CI/CD with GitLab CI or Jenkins.
        - Observability with Prometheus, Grafana, and OpenTelemetry.
        - Scripting proficiency in Bash, Python, or Go.
        - Agile sprint workflow and cross-functional collaboration.
        """
    },
    {
        "page": 2,
        "title": "Data Engineer (Spark & Airflow)",
        "company": "Metrix Data Corp",
        "location": "London, UK",
        "is_remote": False,
        "salary_min": 85000,
        "salary_max": 120000,
        "desc": """
        Build high-throughput ETL data pipelines.
        Requirements:
        - 4+ years of data engineering using Python and SQL.
        - Hands-on experience with Apache Spark, Airflow, and Snowflake or BigQuery.
        - Familiarity with Kafka, PostgreSQL, and AWS S3 data lakes.
        - Data modeling and unit testing with pytest.
        """
    },
    {
        "page": 2,
        # INTENTIONAL DUPLICATE to test Deduplication Engine!
        "title": "Senior Backend Engineer (Python & Cloud)",
        "company": "Nexus Technologies",
        "location": "Bengaluru, India",
        "is_remote": False,
        "salary_min": 140000,
        "salary_max": 180000,
        "desc": """
        We are seeking a Senior Backend Engineer to build scalable microservices.
        Requirements:
        - 5+ years of software engineering experience with Python and FastAPI or Django.
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
