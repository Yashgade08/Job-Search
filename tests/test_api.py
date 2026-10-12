"""
Integration Tests for FastAPI Endpoints
"""

import pytest
from starlette.testclient import TestClient
from api.main import app
from database.connection import init_db

# Initialize database
init_db()
client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "active_database" in data


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database_type" in data


def test_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "total_unique_skills" in data
    assert "active_sources" in data


def test_top_skills_endpoint():
    response = client.get("/api/analytics/skills/top?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "name" in data[0]
        assert "demand_count" in data[0]


def test_role_skill_matrix_endpoint():
    response = client.get("/api/analytics/skills/matrix")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_emerging_tech_endpoint():
    response = client.get("/api/analytics/skills/emerging")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_locations_endpoint():
    response = client.get("/api/analytics/locations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_salaries_endpoint():
    response = client.get("/api/analytics/salaries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_jobs_list_endpoint():
    response = client.get("/api/jobs?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_crawler_adapters_endpoint():
    response = client.get("/api/crawler/adapters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    adapter_ids = [a["id"] for a in data]
    assert "arbeitnow" in adapter_ids
    assert "mock" in adapter_ids


def test_crawler_frontier_endpoint():
    response = client.get("/api/crawler/frontier")
    assert response.status_code == 200
    data = response.json()
    assert "queue_size" in data
