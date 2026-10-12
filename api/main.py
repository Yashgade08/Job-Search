"""
Job Market Skill Demand Intelligence & Crawling Platform API
Main FastAPI Application Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database.connection import init_db, get_active_db_type, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.routes_jobs import router as jobs_router
from api.routes_crawler import router as crawler_router
from api.routes_analytics import router as analytics_router
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created
    init_db()
    # Auto-seed sample intelligence dataset on fresh cloud deployment if database is empty
    try:
        from database.connection import get_session
        from database.models import Job
        with get_session() as _check_sess:
            if _check_sess.query(Job).count() == 0:
                from scripts.seed_data import seed_database
                seed_database()
    except Exception:
        pass
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="Job Market Skill Demand Intelligence API",
    description="Automated Web Crawler, NLP Skill Parser, and Labor Market Analytics Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing (CORS) for Streamlit and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(analytics_router)
app.include_router(jobs_router)
app.include_router(crawler_router)


@app.get("/", tags=["System"])
def root():
    return {
        "service": "Job Market Skill Demand Intelligence API",
        "version": "1.0.0",
        "status": "online",
        "active_database": get_active_db_type(),
        "documentation": "/docs",
        "endpoints": {
            "market_overview": "/api/analytics/overview",
            "top_skills": "/api/analytics/skills/top",
            "skill_matrix": "/api/analytics/skills/matrix",
            "emerging_tech": "/api/analytics/skills/emerging",
            "cooccurrence": "/api/analytics/skills/cooccurrence",
            "locations": "/api/analytics/locations",
            "salaries": "/api/analytics/salaries",
            "jobs_list": "/api/jobs",
            "crawler_adapters": "/api/crawler/adapters",
            "crawler_runs": "/api/crawler/runs",
            "trigger_crawl": "/api/crawler/trigger",
        }
    }


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "database_type": get_active_db_type(),
        "database_status": db_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug_mode)
