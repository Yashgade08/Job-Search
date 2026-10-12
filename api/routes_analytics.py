"""
Market Intelligence and Analytics Endpoints
Provides high-performance aggregation endpoints for skill rankings, role matrices,
co-occurrence graphs, salary trends, and geographic distributions.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db, get_active_db_type
from database.repository import (
    get_market_overview_stats,
    get_top_in_demand_skills,
    get_role_wise_skill_matrix,
    get_emerging_technologies,
    get_city_wise_opportunities,
    get_salary_trends_by_role,
    get_skill_cooccurrence_matrix,
)
from nlp.analytics import calculate_skill_associations
from api.schemas import (
    MarketOverviewResponse,
    SkillDemandItem,
    EmergingTechItem,
    CityOpportunityItem,
    SalaryTrendItem,
)

router = APIRouter(prefix="/api/analytics", tags=["Market Intelligence"])


@router.get("/overview", response_model=MarketOverviewResponse)
def get_market_overview(db: Session = Depends(get_db)):
    """Returns high-level platform KPIs: total jobs, skills, sources, remote %, and avg salary."""
    stats = get_market_overview_stats(db)
    stats["active_db"] = get_active_db_type()
    return stats


@router.get("/skills/top", response_model=List[SkillDemandItem])
def get_top_skills(
    limit: int = Query(25, ge=5, le=100),
    role: Optional[str] = Query(None, description="Filter by canonical role category"),
    category: Optional[str] = Query(None, description="Filter by skill category (e.g. Languages, AI/ML, Cloud/DevOps)"),
    tech_only: bool = Query(False, description="Restrict to technical skills only"),
    db: Session = Depends(get_db)
):
    """Retrieves top in-demand skills ranked by frequency with required qualification percentages."""
    return get_top_in_demand_skills(
        session=db,
        limit=limit,
        role_category=role,
        skill_category=category,
        is_tech_only=tech_only
    )


@router.get("/skills/matrix")
def get_role_skill_matrix(
    top_roles: int = Query(8, ge=2, le=15),
    top_skills: int = Query(10, ge=3, le=20),
    db: Session = Depends(get_db)
):
    """Retrieves cross-tabulation breakdown of top skills mapped to canonical job roles."""
    return get_role_wise_skill_matrix(
        session=db,
        top_roles_count=top_roles,
        top_skills_count=top_skills
    )


@router.get("/skills/emerging", response_model=List[EmergingTechItem])
def get_emerging_tech(
    limit: int = Query(15, ge=5, le=50),
    db: Session = Depends(get_db)
):
    """Identifies high-growth emerging technologies and modern AI/Cloud tech stacks."""
    return get_emerging_technologies(session=db, limit=limit)


@router.get("/skills/cooccurrence")
def get_cooccurrence(
    top_n: int = Query(15, ge=5, le=30),
    db: Session = Depends(get_db)
):
    """
    Computes pair-wise skill co-occurrence matrix, network graph nodes & links,
    and Jaccard association metrics.
    """
    data = get_skill_cooccurrence_matrix(session=db, top_n_skills=top_n)
    associations = calculate_skill_associations(data)
    data["associations"] = associations[:25]
    return data


@router.get("/locations", response_model=List[CityOpportunityItem])
def get_locations(
    limit: int = Query(15, ge=5, le=50),
    db: Session = Depends(get_db)
):
    """Aggregates hiring opportunities and compensation across global tech hubs."""
    return get_city_wise_opportunities(session=db, limit=limit)


@router.get("/salaries", response_model=List[SalaryTrendItem])
def get_salaries(db: Session = Depends(get_db)):
    """Computes salary ranges (min, avg, max) grouped by standardized role categories."""
    return get_salary_trends_by_role(session=db)
