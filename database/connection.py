"""
Database Connection and Session Lifecycle Management
Seamlessly connects to PostgreSQL, with graceful fallback to SQLite for local development.
"""

import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings
from database.models import Base

logger = logging.getLogger("job_crawler.database")
logging.basicConfig(level=logging.INFO)

_engine = None
_SessionFactory = None
_active_db_type = "unknown"


def get_engine():
    global _engine, _SessionFactory, _active_db_type

    if _engine is not None:
        return _engine

    target_url = settings.database_url

    # Check for Streamlit secrets if running in Streamlit Cloud
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
            target_url = str(st.secrets["DATABASE_URL"])
    except Exception:
        pass

    # Normalize PostgreSQL URL for SQLAlchemy compatibility (Render, Neon, Supabase, Railway)
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif target_url.startswith("postgresql://") and not target_url.startswith("postgresql+psycopg2://"):
        target_url = target_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # Check if target is postgres
    if target_url.startswith("postgresql"):
        try:
            logger.info(f"Attempting connection to PostgreSQL at {target_url.split('@')[-1] if '@' in target_url else target_url}")
            engine = create_engine(
                target_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 3},
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to PostgreSQL!")
            _engine = engine
            _active_db_type = "postgresql"
            _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
            return _engine
        except Exception as e:
            if settings.database_fallback_sqlite:
                logger.warning(
                    f"PostgreSQL connection failed ({e}). Falling back to local SQLite database: {settings.sqlite_db_path}"
                )
            else:
                raise e

    # Fallback or default to SQLite
    sqlite_url = f"sqlite:///{settings.sqlite_db_path}"
    logger.info(f"Initializing SQLite engine at {sqlite_url}")
    _engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )
    _active_db_type = "sqlite"
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_active_db_type() -> str:
    """Returns 'postgresql' or 'sqlite'"""
    if _engine is None:
        get_engine()
    return _active_db_type


def init_db():
    """Create all tables in the database if they don't already exist."""
    engine = get_engine()
    logger.info(f"Creating tables in {_active_db_type.upper()}...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_session() -> Session:
    """Create a new database session."""
    if _SessionFactory is None:
        get_engine()
    return _SessionFactory()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """FastAPI dependency for yielding database sessions."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()
