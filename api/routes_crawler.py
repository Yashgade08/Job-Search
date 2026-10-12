"""
Crawler Control and Telemetry Endpoints
"""

import threading
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repository import get_crawler_runs_summary, get_recent_crawl_logs
from crawler.engine import crawl_engine, ADAPTER_REGISTRY
from api.schemas import CrawlTriggerRequest, CrawlRunResponse, CrawlLogItem

router = APIRouter(prefix="/api/crawler", tags=["Crawler Operations"])


@router.get("/adapters")
def list_adapters():
    """Returns available crawler adapters with compliance status."""
    return [
        {
            "id": "arbeitnow",
            "name": "Arbeitnow Permitted Tech Portal",
            "compliance": "Official Authorized Public Feed (100% compliant)",
            "supports_pagination": True,
            "type": "API / HTML Feed"
        },
        {
            "id": "remoteok",
            "name": "RemoteOK Public Engineering Feed",
            "compliance": "Official Authorized Public API",
            "supports_pagination": True,
            "type": "API / JSON"
        },
        {
            "id": "jobicy",
            "name": "Jobicy Remote Tech Jobs API",
            "compliance": "Official Authorized Public API",
            "supports_pagination": True,
            "type": "API / JSON"
        },
        {
            "id": "greenhouse",
            "name": "Company Career Boards (Greenhouse)",
            "compliance": "Public Authorized Career Boards (GitLab, Automattic, Figma, Docker)",
            "supports_pagination": True,
            "type": "Career Page Adapter"
        },
        {
            "id": "naukri",
            "name": "Naukri.com Ethical Adapter",
            "compliance": "Strict robots.txt verification; never bypasses anti-bot/CAPTCHA",
            "supports_pagination": True,
            "type": "Portal Adapter"
        },
        {
            "id": "indeed",
            "name": "Indeed Ethical Adapter",
            "compliance": "Strict robots.txt verification & rate limiting; zero anti-bot bypass",
            "supports_pagination": True,
            "type": "Portal Adapter"
        },
        {
            "id": "foundit",
            "name": "Foundit Ethical Adapter",
            "compliance": "Robots.txt verification & rate limiting",
            "supports_pagination": True,
            "type": "Portal Adapter"
        },
        {
            "id": "mock",
            "name": "Local Mock Portal Test Suite",
            "compliance": "Deterministic Local Test Environment",
            "supports_pagination": True,
            "type": "Test Adapter"
        },
    ]


@router.post("/trigger", response_model=Dict[str, Any])
def trigger_crawl(payload: CrawlTriggerRequest, background_tasks: BackgroundTasks):
    """
    Triggers a live crawl run using the specified adapter.
    Runs asynchronously in the background.
    """
    def run_job():
        crawl_engine.execute_crawl(
            source_name=payload.source,
            max_pages=payload.max_pages,
            query=payload.query
        )

    thread = threading.Thread(target=run_job, daemon=True)
    thread.start()

    return {
        "status": "queued",
        "message": f"Crawl job started in background for source: {payload.source}",
        "max_pages": payload.max_pages,
        "query": payload.query
    }


@router.get("/runs", response_model=List[CrawlRunResponse])
def get_runs(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Retrieves crawl execution history and metrics."""
    return get_crawler_runs_summary(db, limit=limit)


@router.get("/runs/{run_id}/logs", response_model=List[CrawlLogItem])
def get_run_logs(run_id: int, limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    """Retrieves granular audit logs for a specific crawl run."""
    return get_recent_crawl_logs(db, run_id=run_id, limit=limit)


@router.get("/frontier")
def get_frontier_stats():
    """Returns in-memory Crawl Frontier queue state and telemetry."""
    return crawl_engine.frontier.stats()
