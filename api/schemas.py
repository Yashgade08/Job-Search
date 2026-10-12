"""
Pydantic Schemas for API Requests, Responses, and Intelligence Models
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JobSummary(BaseModel):
    id: int
    job_title: str
    normalized_title: str
    role_category: str
    company: str
    city: Optional[str] = None
    country: Optional[str] = None
    is_remote: bool
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    experience_level: Optional[str] = None
    posting_date: Optional[datetime] = None
    source_portal: str
    job_url: str
    extracted_skills_count: int

    class Config:
        from_attributes = True


class JobDetail(JobSummary):
    description_cleaned: str
    raw_html: Optional[str] = None
    canonical_url: str
    created_at: Optional[datetime] = None
    extracted_skills: List[Dict[str, Any]] = []


class SkillDemandItem(BaseModel):
    id: int
    name: str
    category: str
    is_tech: bool
    demand_count: int
    required_count: int
    required_pct: float
    market_share_pct: float
    avg_salary: Optional[float] = None


class EmergingTechItem(BaseModel):
    name: str
    category: str
    demand_count: int
    avg_salary: Optional[float] = None
    momentum_index: float


class CityOpportunityItem(BaseModel):
    city: str
    country: str
    job_count: int
    remote_count: int
    avg_salary: Optional[float] = None


class SalaryTrendItem(BaseModel):
    role: str
    sample_size: int
    min_salary: float
    max_salary: float
    avg_salary: float


class CrawlTriggerRequest(BaseModel):
    source: str = Field(default="arbeitnow", description="Source name: arbeitnow, remoteok, jobicy, greenhouse, naukri, indeed, foundit, mock")
    max_pages: int = Field(default=2, ge=1, le=20)
    query: str = Field(default="", description="Optional keyword query filter")


class CrawlRunResponse(BaseModel):
    id: int
    run_uuid: str
    source_name: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float
    urls_discovered: int
    pages_crawled: int
    jobs_extracted: int
    duplicates_skipped: int
    errors_count: int
    http_200_count: int
    http_429_count: int
    error_summary: Optional[str] = None


class CrawlLogItem(BaseModel):
    id: int
    run_id: int
    timestamp: str
    level: str
    message: str
    status_code: Optional[int] = None
    url: Optional[str] = None
    error_type: Optional[str] = None


class MarketOverviewResponse(BaseModel):
    total_jobs: int
    total_unique_skills: int
    active_sources: int
    total_companies: int
    remote_percentage: float
    average_salary_usd: Optional[float] = None
    active_db: str
