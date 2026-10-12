"""
Application Configuration and Settings Module
Handles environment variables, crawler politeness defaults, and database targets.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/job_market_db",
        alias="DATABASE_URL",
    )
    database_fallback_sqlite: bool = Field(default=True, alias="DATABASE_FALLBACK_SQLITE")
    sqlite_db_path: str = Field(
        default=str(BASE_DIR / "job_market.db"),
        alias="SQLITE_DB_PATH",
    )

    # Crawler Politeness & Frontier Defaults
    default_user_agent: str = Field(
        default="JobDemandBot/1.0 (+https://github.com/job-intelligence/crawler; polite job market intelligence researcher)",
        alias="DEFAULT_USER_AGENT",
    )
    default_download_delay_seconds: float = Field(default=2.0, alias="DEFAULT_DOWNLOAD_DELAY_SECONDS")
    max_download_delay_seconds: float = Field(default=10.0, alias="MAX_DOWNLOAD_DELAY_SECONDS")
    max_concurrent_requests_per_domain: int = Field(default=1, alias="MAX_CONCURRENT_REQUESTS_PER_DOMAIN")
    request_timeout_seconds: int = Field(default=15, alias="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    backoff_factor: float = Field(default=2.0, alias="BACKOFF_FACTOR")
    obey_robots_txt: bool = Field(default=True, alias="OBEY_ROBOTS_TXT")
    store_raw_html: bool = Field(default=True, alias="STORE_RAW_HTML")
    max_crawl_pages_default: int = Field(default=20, alias="MAX_CRAWL_PAGES_DEFAULT")

    # API & Dashboard
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    dashboard_port: int = Field(default=8501, alias="DASHBOARD_PORT")
    debug_mode: bool = Field(default=True, alias="DEBUG_MODE")

    # NLP Settings
    skill_extraction_confidence_threshold: float = Field(default=0.75, alias="SKILL_EXTRACTION_CONFIDENCE_THRESHOLD")
    max_extracted_skills_per_job: int = Field(default=35, alias="MAX_EXTRACTED_SKILLS_PER_JOB")

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
