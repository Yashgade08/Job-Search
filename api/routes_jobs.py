"""
Job Exploration and Details Endpoints
"""

import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.connection import get_db
from database.models import Job, JobSkill, Skill
from api.schemas import JobSummary, JobDetail

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobSummary])
def list_jobs(
    query: Optional[str] = Query(None, description="Search keyword in title, company, or description"),
    role: Optional[str] = Query(None, description="Filter by role category"),
    city: Optional[str] = Query(None, description="Filter by city"),
    source: Optional[str] = Query(None, description="Filter by portal source"),
    remote_only: bool = Query(False, description="Filter remote positions only"),
    experience: Optional[str] = Query(None, description="Filter by experience tier"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    q = db.query(Job)

    if query:
        pattern = f"%{query}%"
        q = q.filter(
            (Job.job_title.ilike(pattern)) |
            (Job.company.ilike(pattern)) |
            (Job.description_cleaned.ilike(pattern))
        )
    if role and role != "All":
        q = q.filter(Job.role_category == role)
    if city and city != "All":
        q = q.filter(Job.city == city)
    if source and source != "All":
        q = q.filter(Job.source_portal == source)
    if remote_only:
        q = q.filter(Job.is_remote == True)
    if experience and experience != "All":
        q = q.filter(Job.experience_level == experience)

    jobs = q.order_by(desc(Job.posting_date)).offset(offset).limit(limit).all()
    return jobs


@router.get("/export/csv")
def export_jobs_csv(
    role: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generates and streams a CSV of filtered jobs with extracted skills."""
    q = db.query(Job)
    if role and role != "All":
        q = q.filter(Job.role_category == role)
    if source and source != "All":
        q = q.filter(Job.source_portal == source)

    jobs = q.order_by(desc(Job.created_at)).limit(500).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Job Title", "Normalized Title", "Role Category", "Company",
        "City", "Country", "Remote", "Salary Min", "Salary Max",
        "Experience Level", "Source Portal", "Job URL", "Posting Date"
    ])

    for j in jobs:
        writer.writerow([
            j.id, j.job_title, j.normalized_title, j.role_category, j.company,
            j.city or "", j.country or "", j.is_remote, j.salary_min or "", j.salary_max or "",
            j.experience_level or "", j.source_portal, j.job_url, j.posting_date or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=job_market_demand.csv"}
    )


@router.get("/{job_id}", response_model=JobDetail)
def get_job_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Fetch skills
    skills_query = (
        db.query(Skill.name, Skill.category, Skill.is_tech_skill, JobSkill.is_required, JobSkill.confidence)
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .filter(JobSkill.job_id == job.id)
        .all()
    )

    extracted_skills = [
        {
            "name": s.name,
            "category": s.category,
            "is_tech": s.is_tech_skill,
            "is_required": s.is_required,
            "confidence": s.confidence
        }
        for s in skills_query
    ]

    detail = JobDetail(
        id=job.id,
        job_title=job.job_title,
        normalized_title=job.normalized_title,
        role_category=job.role_category,
        company=job.company,
        city=job.city,
        country=job.country,
        is_remote=job.is_remote,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        experience_level=job.experience_level,
        posting_date=job.posting_date,
        source_portal=job.source_portal,
        job_url=job.job_url,
        extracted_skills_count=len(extracted_skills),
        description_cleaned=job.description_cleaned,
        raw_html=job.raw_html,
        canonical_url=job.canonical_url,
        created_at=job.created_at,
        extracted_skills=extracted_skills
    )
    return detail
