"""
SQLAlchemy ORM Data Models for Job Intelligence & Crawling Operations
Supports both PostgreSQL (primary) and SQLite (automatic fallback)
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Job(Base):
    """
    Main job listing record with raw and normalized attributes
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)
    
    # Original Attributes
    job_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False, index=True)
    location_raw = Column(String(255), nullable=True)
    
    # Normalized Title & Role
    normalized_title = Column(String(255), nullable=False, index=True)
    role_category = Column(String(100), nullable=False, index=True)  # e.g., Backend Developer, Data Scientist
    
    # Normalized Geography
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    is_remote = Column(Boolean, default=False, index=True)
    
    # Compensation
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    salary_period = Column(String(20), nullable=True)  # yearly, monthly, hourly
    
    # Experience Level
    experience_min_years = Column(Float, nullable=True)
    experience_max_years = Column(Float, nullable=True)
    experience_level = Column(String(50), nullable=True, index=True)  # Entry, Mid, Senior, Lead, Executive
    
    # Descriptions
    description_raw = Column(Text, nullable=True)
    description_cleaned = Column(Text, nullable=False)
    raw_html = Column(Text, nullable=True)
    
    # Metadata & URLs
    posting_date = Column(DateTime, nullable=True, index=True)
    job_url = Column(Text, nullable=False)
    canonical_url = Column(String(1000), nullable=False, index=True)
    source_portal = Column(String(100), nullable=False, index=True)
    
    # Crawl / Pipeline Tracking
    crawl_run_id = Column(Integer, ForeignKey("crawl_runs.id", ondelete="SET NULL"), nullable=True)
    extracted_skills_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    crawl_run = relationship("CrawlRun", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.id}: {self.job_title} at {self.company} ({self.source_portal})>"


class Skill(Base):
    """
    Standardized skill entity
    """
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    normalized_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # Languages, Frameworks, Cloud/DevOps, Databases, AI/ML, Tools, Soft Skills
    is_tech_skill = Column(Boolean, default=True, index=True)
    aliases = Column(Text, nullable=True)  # Comma-separated alternative names / aliases
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job_skills = relationship("JobSkill", back_populates="skill")

    def __repr__(self):
        return f"<Skill {self.name} [{self.category}]>"


class JobSkill(Base):
    """
    Association table between Jobs and Skills with requirement classification & extraction confidence
    """
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    is_required = Column(Boolean, default=True, index=True)  # True = Required/Must-have, False = Preferred/Bonus
    confidence = Column(Float, default=1.0)
    occurrence_count = Column(Integer, default=1)
    extracted_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint so a skill is only mapped once per job
    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )

    # Relationships
    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill", back_populates="job_skills")

    def __repr__(self):
        return f"<JobSkill job={self.job_id} skill={self.skill_id} required={self.is_required}>"


class CrawlRun(Base):
    """
    Crawl job execution run record tracking execution performance and error telemetry
    """
    __tablename__ = "crawl_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_uuid = Column(String(64), unique=True, nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)  # arbeitnow, remoteok, greenhouse, portal_search, mock
    status = Column(String(30), default="pending", index=True)     # pending, running, completed, failed, stopped
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    
    # Frontier & Extraction Metrics
    urls_discovered = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)
    jobs_extracted = Column(Integer, default=0)
    duplicates_skipped = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    average_page_time_ms = Column(Float, default=0.0)
    
    # HTTP Status Telemetry
    http_200_count = Column(Integer, default=0)
    http_429_count = Column(Integer, default=0)
    http_other_count = Column(Integer, default=0)
    error_summary = Column(Text, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="crawl_run")
    logs = relationship("CrawlLog", back_populates="crawl_run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CrawlRun {self.id} [{self.source_name}] - {self.status}>"


class CrawlLog(Base):
    """
    Detailed audit log of each crawl event, request attempt, error, or retry
    """
    __tablename__ = "crawl_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("crawl_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(10), default="INFO", index=True)  # INFO, WARNING, ERROR, DEBUG
    url = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    error_type = Column(String(100), nullable=True)

    # Relationships
    crawl_run = relationship("CrawlRun", back_populates="logs")

    def __repr__(self):
        return f"<CrawlLog [{self.level}] {self.message[:40]}>"


class CrawlFrontierItem(Base):
    """
    Frontier persistence table for distributed or resumable crawl queue state
    """
    __tablename__ = "crawl_frontier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    canonical_url = Column(String(1000), unique=True, nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    priority = Column(Integer, default=10, index=True)
    depth = Column(Integer, default=0)
    status = Column(String(20), default="queued", index=True)  # queued, crawled, failed, skipped
    retry_count = Column(Integer, default=0)
    http_status = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    crawled_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<FrontierItem {self.canonical_url[:50]} status={self.status}>"
